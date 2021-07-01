# -*- coding: utf-8 -*-

from webs.api.exceptions.customs import RecordNotFound
from webs.api.models.db_proxy import server_model_proxy, task_model_proxy, subtask_model_proxy, url_model_proxy, \
    schedule_task_proxy, task_url_model_proxy, result_model_proxy
from worker import celery_app
from worker.library.helper import split_urls, send, WeightedRandomGenerator, remove_files


@celery_app.task(name='delivery_task')
def delivery_task(task_id):
    """
    下发任务
    :param task_id:
    :return:
    """

    task_obj = task_model_proxy.find(id=task_id)
    if not task_obj:
        return

    # 增加爬虫任务调度记录
    schedule_task_obj = task_model_proxy.add_schedule_record(
        task_id=task_id, schedule_task_status="start_delivery", crawl_options=task_obj.crawl_options)
    schedule_task_id = schedule_task_obj.id

    # 查询待爬取的url struct列表
    urls_struct = task_url_model_proxy.query_urls_by_task_id(task_id)

    # url分块处理
    chunk_urls_struct = split_urls(urls_struct)

    # 获取爬虫节点服务器配额
    servers_info = server_model_proxy.query_servers_by_score(sort='desc')
    if not servers_info:
        task_model_proxy.set_many_attr(obj_id=task_id, fields_v={'task_status': 'No server found！', 'finished': True})
        raise RecordNotFound('No server found！')

    ###### 投递子任务
    # 当url分块数小于服务器节点数时采用轮询算法
    if len(chunk_urls_struct) <= len(servers_info):
        for index, chunk_url_struct in enumerate(chunk_urls_struct):
            send(schedule_task_id, chunk_url_struct, servers_info[index], task_obj.crawl_options)

    # 否则使用加权随机算法
    else:
        server_seeds = WeightedRandomGenerator(servers_info)
        for chunk_url_struct in chunk_urls_struct:
            send(schedule_task_id, chunk_url_struct, server_seeds.spawn(), task_obj.crawl_options)

    ###### 根据子任务发送情况设置主任务状态
    # 查询子任务投递失败数
    failure_count = subtask_model_proxy.query_delivery_failure_count(schedule_task_id)
    # 如果子任务投递全部失败，则设置当前调度任务为投递失败状态
    if failure_count == len(chunk_urls_struct):
        schedule_task_proxy.set_many_attr(
            obj_id=schedule_task_id, fields_v={'schedule_task_status': 'delivery_failure', 'finished': True}
        )
        # 如果是临时任务，则直接标记主任务为失败状态
        if task_obj.schedule_options.get('schedule_type') == 'instantly':
            task_model_proxy.set_many_attr(
                obj=task_obj, fields_v={'task_status': 'delivery_failure', 'finished': True}
            )

    # 只要有一个投递失败，则标记为部分失败
    elif failure_count != 0:
        schedule_task_proxy.set_attr_by_id(
            obj_id=schedule_task_id, field='schedule_task_status', value='part_delivery_failure')

    # 否则标记全部投递成功
    else:
        schedule_task_proxy.set_attr_by_id(
            obj_id=schedule_task_id, field='schedule_task_status', value='delivery_success')


@celery_app.task(name='delete_task')
def delete_task(task_id):
    """
    删除任务，因需要删除截图和har文件 故使用异步方式进行删除
    :param task_id:
    :return:
    """

    # 查询所有schedule task
    schedule_task_subquery = schedule_task_proxy.db_session.query(schedule_task_proxy.model.id) \
        .filter(schedule_task_proxy.model.task_id == task_id).subquery()

    # 查询所有subtask
    subtask_subquery = subtask_model_proxy.db_session.query(subtask_model_proxy.model.id).filter(
        subtask_model_proxy.model.schedule_task_id.in_(schedule_task_subquery)).subquery()

    ###### 删除结果
    result_query = result_model_proxy.self_session.filter(
        result_model_proxy.model.subtask_id.in_(subtask_subquery))

    # 删除截图
    screenshot_ids = [each.screenshot_id + '.png' for each in
                      result_query.filter(result_model_proxy.model.screenshot_id.isnot(None)).all()]
    remove_files(path='screenshots', file_ids=screenshot_ids)

    # 删除hars
    har_ids = [each.har_uuid + '.json' for each in
               result_query.filter(result_model_proxy.model.har_uuid.isnot(None)).all()]
    remove_files(path='hars', file_ids=har_ids)

    # 删除结果
    result_query.delete(synchronize_session=False)
    result_model_proxy.safe_commit()

    # 删除Schedule task
    schedule_task_proxy.delete_models(ids=schedule_task_subquery, fields='id')

    # 删除subtask
    subtask_model_proxy.delete_models(ids=subtask_subquery, fields='id')

    # 删除task_url
    task_url_model_proxy.delete_model(task_id=task_id)

# -*- coding: utf-8 -*-


from rpyc import ThreadedServer

from aps.server import apscheduler_server, APSchedulerService


def runserver():
    """运行APSchedule RPC服务"""

    # 在后台运行APS
    apscheduler_server.start()

    # 启动RPC承载APScheduler
    server = ThreadedServer(
        APSchedulerService, port=15003,
        protocol_config={'allow_public_attrs': True, 'allow_pickle': True})

    # 启动RPC服务
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        apscheduler_server.shutdown()


if __name__ == '__main__':
    runserver()

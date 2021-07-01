#!/bin/sh

# web服务
if [ "$ENDPOINT" = "web" ]; then
    # 开发环境
  if [ "$FLASK_ENV" = "development" ]; then
    flask run -h 0.0.0.0 -p 5000

  # 生产环境
  elif [ "$FLASK_ENV" = "production" ]; then
    python build_sentry_ini.py
    gunicorn --worker-tmp-dir /dev/shm --log-config gunicorn_logging.ini -c gunicorn_config.py manage:app
  fi

# 爬取
elif [ "$ENDPOINT" = "fetch" ]; then
    # 开启虚拟显示器
  echo "开启xvfb"
  rm -rf /tmp/.X99-lock
  Xvfb -screen 0 1020x720x16 :99 &
  export DISPLAY=:99
  celery -A worker.celery_app worker -Q priority_fetch -l info -c $WORK_MAX_COUNT --prefetch-multiplier 1 --max-tasks-per-child 1 -n crawl_fetch@%h

# 保存结果
elif [ "$ENDPOINT" = "results" ]; then
#    celery -A worker.celery_app worker -Q results -l info -c 5 --prefetch-multiplier 4 --max-tasks-per-child 100 -n results@%h
    celery -A worker.celery_app worker -Q results -l info --pool=prefork --concurrency=5 --without-heartbeat --prefetch-multiplier 4 --max-tasks-per-child 100 -n results@%h
fi

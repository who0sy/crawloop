#!/bin/sh

# web服务
if [ "$ENDPOINT" = "web" ]; then
    # 开发环境
  if [ "$FLASK_ENV" = "development" ]; then
    flask run -h 0.0.0.0 -p 5000

  # 生产环境
  elif [ "$FLASK_ENV" = "production" ]; then

    # 注册sentry
    python build_sentry_ini.py

    # 使用gunicorn承载flask服务
    gunicorn --worker-tmp-dir /dev/shm --log-config gunicorn_logging.ini -c gunicorn_config.py manage:app
  fi

# grpc服务端
elif [ "$ENDPOINT" = "engine-grpc" ]; then
  python grpcserver.py

# Apscheduler
elif [ "$ENDPOINT" = "apscheduler" ]; then
  python apserver.py

# worker
elif [ "$ENDPOINT" = "engine-worker" ]; then
#  celery -A worker.celery_app worker -Q engine,base_result -l info -c 5 -n worker_engine@%h
  celery -A worker.celery_app worker -Q engine,base_result -l info --pool=prefork --concurrency=10 --prefetch-multiplier 4  --without-heartbeat -n worker_engine@%h
fi

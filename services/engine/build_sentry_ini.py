# -*- coding: utf-8 -*-

import json
import os

from configobj import ConfigObj

log_ini = ConfigObj("gunicorn_logging.ini", encoding='UTF8')
log_ini['handler_sentry']['args'] = json.dumps((os.getenv('SENTRY_DSN'),), ensure_ascii=False)
log_ini.write()

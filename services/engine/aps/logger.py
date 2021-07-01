# -*- coding: utf-8 -*-

import logging

scheduler_logger = logging.getLogger('scheduler')
stream_handler = logging.StreamHandler()
fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
stream_handler.setFormatter(fmt)
scheduler_logger.addHandler(stream_handler)  # 输出到终端
scheduler_logger.setLevel(logging.INFO)

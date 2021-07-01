# -*- coding: utf-8 -*-

import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class ProxyServer(TypedDict):
    server: str
    bypass: Optional[str]
    username: Optional[str]
    password: Optional[str]


class RecordHarOptions(TypedDict):
    omitContent: Optional[bool]
    path: str

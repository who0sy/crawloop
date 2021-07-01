# -*- coding: utf-8 -*-

from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import setup
from setuptools.extension import Extension

setup(
    ext_modules=cythonize(
        [
            Extension('rpc.*', ['rpc/*.py']),
            Extension('rpc.client.*', ['rpc/client/*.py']),
            Extension('rpc.pb.*', ['rpc/pb/*.py']),
            Extension('rpc.server.*', ['rpc/server/*.py']),
            Extension('webs.*', ['webs/*.py']),
            Extension('webs.api.*', ['webs/api/*.py']),
            Extension('webs.api.bizs.*', ['webs/api/bizs/*.py']),
            Extension('webs.api.exceptions.*', ['webs/api/exceptions/*.py']),
            Extension('webs.api.models*', ['webs/api/models/*.py']),
            Extension('webs.api.models.db_proxy.*', ['webs/api/models/db_proxy/*.py']),
            Extension('webs.api.schemas.*', ['webs/api/schemas/*.py']),
            Extension('webs.api.utils.*', ['webs/api/utils/*.py']),
            Extension('webs.api.views.*', ['webs/api/views/*.py']),
            Extension('webs.core.*', ['webs/core/*.py']),
            Extension('webs.core.requests.*', ['webs/core/requests/*.py']),
            Extension('worker.*', ['worker/*.py']),
            Extension('worker.library.*', ['worker/library/*.py'])
        ],
        build_dir='build',
        compiler_directives=dict(
            always_allow_keywords=True, language_level=3
        )
    ),
    cmdclass=dict(
        build_ext=build_ext
    )
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import config
import traceback
from aioVextractor.utils.exception import http_exception
import wrapt
import functools


def RequestRetry(wrapped=None,
                 default_exception_return=False,
                 default_other_exception_return=False):
    if wrapped is None:
        return functools.partial(RequestRetry,
                                 default_exception_return=default_exception_return,
                                 default_other_exception_return=default_other_exception_return)

    @wrapt.decorator
    async def wrapper(func, instance, args, kwargs):

        for _ in range(config.RETRY):
            try:
                return await func(*args, **kwargs)
            except http_exception:
                traceback.print_exc()
                continue
            except:
                traceback.print_exc()
                return default_other_exception_return
        else:
            return default_exception_return

    return wrapper(wrapped)

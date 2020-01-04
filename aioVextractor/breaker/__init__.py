#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from aioVextractor.breaker.base_breaker import (
    BaseBreaker,
)
from aioVextractor.breaker.base_breaker import validate as BreakerValidater
from aioVextractor.breaker.breakers import *

_ALL_CLASSES = [
    klass
    for name, klass in globals().items()
    if name.endswith('BK') and name not in {"baseBK"}
]
# _ALL_CLASSES.append(baseBK)


def gen_breaker_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_CLASSES


# __all__ = [
#     "BaseBreaker",
#     "BreakerValidater",
#     "vimeo",
#     "xinpianchang",
#     "youtube",
#     "instagram",
#     "pinterest",
#     "gen_breaker_classes",
# ]

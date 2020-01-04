#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/4/19
# IDE: PyCharm

from aioVextractor.rss.base_rss import validate as RssValidater
from aioVextractor.rss.base_rss import (
    BaseRss,
    RequestRetry,
)
from aioVextractor.rss.rss import *


_ALL_CLASSES = [
    klass
    for name, klass in globals().items()
    if name.endswith('Rss') and name not in {"BaseRss"}
]

def gen_rss_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_CLASSES

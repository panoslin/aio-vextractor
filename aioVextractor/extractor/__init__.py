#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm
"""
extractor/ contains all the codes necessary for each specified website
every extractor listed under this dir are inherit from extractor.base_extractor.BaseExtractor,
which having a bunch of easy-to-use APIs.
Such as:
1. general_headers: provides a headers while requesting a webpage
2. random_ua: gives out a random user agent
3. extract_iframe: An API to extract iframe with src link to v.qq / youku / youtube / vimeo and etc.
4. janitor: match the url(s) from string using regex
5. merge_dicts: shows a different way to merge two dict other from {**dict_one, **dict_two}
6. unescape: unescape a string
and etc..

If you want to add extractor in this file, here remember the following points:
1. Regenerate file extractor.extractors
2. specify target_website as class variable
3. inherit BaseExtractor.__init__() and define self.from_
4. redefine BaseExtractor.entracne()

"""

from aioVextractor.extractor.extractors import *

_ALL_CLASSES = [
    klass
    for name, klass in globals().items()
    if name.endswith('IE') and name not in {"baseIE", "commonIE"}
]
_ALL_CLASSES.append(commonIE)
# _ALL_CLASSES.append(baseIE)

def gen_extractor_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_CLASSES

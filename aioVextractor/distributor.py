#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

from aioVextractor.extractor import gen_extractor_classes
from aioVextractor.breaker import gen_breaker_classes


def distribute_webpage(webpage_url):
    """
    Search for the suitable existed InfoExtractor

    :return:
    Extractor: An instance of Extractor if suitable InfoExtractor existed
    str: "No suitable InfoExtractor is provided" if no suitable InfoExtractor
    """
    for ie in gen_extractor_classes():
        if ie.suitable(webpage_url):
            return ie
        else:
            continue
    else:
        return "No suitable InfoExtractor is provided"


def distribute_playlist(webpage_url):
    """
    Search for the suitable existed Breaker

    :return:
    Extractor: An instance of Breaker if suitable Breaker existed
    str: "No suitable Breaker is provided" if no suitable Breaker
    """
    for bk in gen_breaker_classes():
        if bk.suitable(webpage_url):
            return bk
        else:
            continue
    else:
        return "No suitable Breaker is provided"


def distribute_hybrid(webpage_url):
    """
    Search for the suitable existed Extractor/Breaker

    :return:
    Extractor: An instance of Extractor/Breaker if suitable Extractor/Breaker existed
    str: "No suitable Extractor/Breaker is provided" if no suitable Extractor/Breaker
    """
    for instance in gen_extractor_classes()[:-1] + gen_breaker_classes() + gen_extractor_classes()[-1:]:
        if instance.suitable(webpage_url):
            return instance
        else:
            continue
    else:
        return "No suitable Extractor/Breaker is provided"


if __name__ == '__main__':
    pass

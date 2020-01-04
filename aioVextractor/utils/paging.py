#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import math

def pager(cursor, offset, step=10):
    """

    :param cursor: current place
    :param offset: page size
    :param step: response page size
    :return:
    """
    offset = math.ceil(float(offset / step)) * step  ## limit it to be the integer multiple of 10
    for page in range((cursor + step) // step, (cursor + offset) // step + 1):
        yield page


if __name__ == '__main__':
    for _ in pager(5, 61, 20):
        print(_)

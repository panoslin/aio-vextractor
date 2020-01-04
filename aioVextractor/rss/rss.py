#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/10/20
# IDE: PyCharm
"""
HOW TO GENERATE THIS FILE:
import os
rss_path = "/path/to/rss"
res = [ele for ele in os.listdir(rss_path) if ele not in {'__init__.py', '__pycache__', 'rss.py'}]
for ele in res:
    print(f"from aioVextractor.rss.{ele.replace('.py', '')} import Rss as {ele.replace('.py', '')}Rss")

"""
from aioVextractor.rss.base_rss import BaseRss
from aioVextractor.rss.xinpianchang import Rss as xinpianchangRss
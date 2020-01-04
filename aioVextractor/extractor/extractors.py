#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/10/20
# IDE: PyCharm
"""
HOW TO GENERATE THIS FILE:
import os
extractor_path = "/path/to/extractor"
res = [ele for ele in os.listdir(extractor_path) if ele not in {'__init__.py', 'extractors.py', '__pycache__'}]
for ele in res:
    print(f"from aioVextractor.extractor.{ele.replace('.py', '')} import Extractor as {ele.replace('.py', '')}IE")

"""
from aioVextractor.extractor.base_extractor import BaseExtractor as baseIE
from aioVextractor.extractor.adquan import Extractor as adquanIE
from aioVextractor.extractor.behance import Extractor as behanceIE
from aioVextractor.extractor.bilibili import Extractor as bilibiliIE
from aioVextractor.extractor.carben import Extractor as carbenIE
from aioVextractor.extractor.common import Extractor as commonIE
from aioVextractor.extractor.digitaling import Extractor as digitalingIE
from aioVextractor.extractor.douyin import Extractor as douyinIE
from aioVextractor.extractor.eyepetizer import Extractor as eyepetizerIE
from aioVextractor.extractor.hellorf import Extractor as hellorfIE
from aioVextractor.extractor.instagram import Extractor as instagramIE
from aioVextractor.extractor.iwebad import Extractor as iwebadIE
from aioVextractor.extractor.lanfan import Extractor as lanfanIE
from aioVextractor.extractor.music163 import Extractor as music163IE
from aioVextractor.extractor.naver import Extractor as naverIE
from aioVextractor.extractor.pinterest import Extractor as pinterestIE
from aioVextractor.extractor.renren import Extractor as renrenIE
from aioVextractor.extractor.socialbeta import Extractor as socialbetaIE
from aioVextractor.extractor.taopiaopiao import Extractor as taopiaopiaoIE
from aioVextractor.extractor.tencent import Extractor as tencentIE
from aioVextractor.extractor.toutiao import Extractor as toutiaoIE
from aioVextractor.extractor.tvcf import Extractor as tvcfIE
from aioVextractor.extractor.vimeo import Extractor as vimeoIE
from aioVextractor.extractor.vmovier import Extractor as vmovierIE
from aioVextractor.extractor.weibo import Extractor as weiboIE
from aioVextractor.extractor.weixin import Extractor as weixinIE
from aioVextractor.extractor.xiaohongshu import Extractor as xiaohongshuIE
from aioVextractor.extractor.xinpianchang import Extractor as xinpianchangIE
from aioVextractor.extractor.youku import Extractor as youkuIE
from aioVextractor.extractor.youtube import Extractor as youtubeIE
from aioVextractor.extractor.xiami import Extractor as xiamiIE
from aioVextractor.extractor.qqmusic import Extractor as qqmusicIE
from aioVextractor.extractor.douban import Extractor as doubanIE
from aioVextractor.extractor.maoyan import Extractor as maoyanIE
from aioVextractor.extractor.weishi import Extractor as weishiIE


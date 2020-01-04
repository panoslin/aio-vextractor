#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import re
import traceback

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import time
# from pyppeteer.errors import NetworkError
# import asyncio
import os


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://movie\.douban\.com/trailer/\d{6}/",
        "https://movie\.douban.com/trailer/\d{6}/?trailer_id=\d{6}&trailer_type=A",
    ]

    TEST_CASE = [
        "https://movie.douban.com/trailer/256281/",
        "https://movie.douban.com/trailer/255831/",
        "https://movie.douban.com/trailer/255756/",
        "https://movie.douban.com/trailer/118461/?trailer_id=118461&trailer_type=A",
        "https://movie.douban.com/trailer/255756/?trailer_id=255756&trailer_type=A",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "douban"


    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua()),
        )
        results = self.extract_page(response=response)
        return results

    def extract_page(self,response):
        selector = self.Selector(text=response)
        result = {
            "play_addr": os.path.join(selector.css("source::attr(src)").extract_first()),
            "title": selector.css("title::text").extract_first().lstrip().replace("\n",""),
            "cover": re.findall('<li id="v_0"[\s\S]*?<img src="(.*?)" height',response)[0].strip("?"),
            "vid": re.findall('"target-id" value="(.*?)"',response)[0],
        }
        return result

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

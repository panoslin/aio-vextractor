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
        "http[s]?://m\.maoyan\.com/movie/\d{7}/preview.*",
        "http[s]?://m\.maoyan\.com/prevue/.*",
    ]

    TEST_CASE = [
        "http://m.maoyan.com/movie/1227006/preview",
        "http://m.maoyan.com/movie/1217041/preview",
        "http://m.maoyan.com/movie/1257417/preview",
        "http://m.maoyan.com/movie/1217125/preview?_v_=yes&videoId=386832&share=Android",
        "http://m.maoyan.com/prevue/386525?share=Android",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "maoyan"


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
            "play_addr": os.path.join("http://", selector.css("video::attr(src)").extract_first().lstrip("//")),
            "title": selector.css("title::text").extract_first(),
            "vid": re.findall('mp4","movieId":(\d*?),',response)[0],
            "cover": os.path.join(selector.css("video::attr(poster)").extract_first().lstrip("//")),
        }
        return result

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

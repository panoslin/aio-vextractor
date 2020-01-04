#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import re
import asyncio

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import time



class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://y\.qq\.com/n/yqq/mv/v/\w{10,15}\.html",
    ]

    TEST_CASE = [
        "Memories (歌词版) https://y.qq.com/n/yqq/mv/v/o0032i34nid.html",
        "2019年第47期：易烊千玺肖战新歌上榜《桥边姑娘》《下山》创前十 https://y.qq.com/n/yqq/mv/v/013BpZIz1An63j.html",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "QQ音乐"
        self.results = []
        self.last_response = time.time()


    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        browser = await self.launch_browers()
        page = await browser.newPage()
        await page.goto(webpage_url)
        html = await page.content()
        mv__name = self.Selector(text=html).css('.mv__name::text').extract_first()
        while mv__name is None and time.time() - self.last_response < 5:
            await asyncio.sleep(0.1)
        else:
            page_text = await page.content()
            print(page_text)
            await browser.close()
            self.extract_page(response=page_text)
            return self.results

    def extract_page(self, response):
        selector = self.Selector(text=response)
        result = {
            "play_addr": selector.css("video::attr(src)").extract_first(),
            "title": selector.css("title::text").extract_first(),
            "vid": re.findall('window.location.replace.*?mv&vid=(.*?)"\)',response)[0],
            "cover": re.findall('<img alt.*?src="(.*?)">',response)[0],
            "view_count": re.findall('<span class="mv__listen">播放量：(.*?)</span>',response)[0],
                  }
        self.results.append(result)

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import re
import jmespath
import os
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import time
from pyppeteer.errors import NetworkError
import asyncio
import json


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://h5\.m\.taopiaopiao\.com/app/movie/pages/index/show-preview.html.*",
        "http[s]?://h5\.m\.taopiaopiao\.com/app/dianying/pages/mini-video/index.html.*",
        "http[s]?://h5\.m\.taopiaopiao\.com/app/dianying/pages/show-preview/index.html.*",
    ]

    TEST_CASE = [
        "http://h5.m.taopiaopiao.com/app/movie/pages/index/show-preview.html?showid=180169&previewid=240796884668",
        "https://h5.m.taopiaopiao.com/app/dianying/pages/mini-video/index.html?tbVideoId=244895745395&videoId=1567428&type=8&cityCode=440100",
        "https://h5.m.taopiaopiao.com/app/dianying/pages/mini-video/index.html?tbVideoId=244845440970&videoId=1567601&type=8&cityCode=440100",
        "https://h5.m.taopiaopiao.com/app/dianying/pages/mini-video/index.html?tbVideoId=244637816398&videoId=1567210&type=8&cityCode=440100",
        "http://h5.m.taopiaopiao.com/app/movie/pages/index/show-preview.html?showid=1211803&previewid=245165739831",
        "https://h5.m.taopiaopiao.com/app/dianying/pages/show-preview/index.html?showid=1279058&previewid=237152859603",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "taopiaopiao"
        self.results = []
        self.last_response = time.time()

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        browser = await self.launch_browers()
        page = await browser.newPage()
        page.on('response', self.intercept_response)
        await page.goto(webpage_url)
        if re.match("http[s]?://h5\.m\.taopiaopiao\.com/app/movie/pages/index/show-preview.html.*", webpage_url) or \
                re.match("http[s]?://h5\.m\.taopiaopiao\.com/app/dianying/pages/show-preview/index.html.*", webpage_url):
            await asyncio.sleep(1)
            response_text = await page.content()
            self.extract_page(response=response_text)
        else:
            while not self.results and time.time() - self.last_response < 3:
                await asyncio.sleep(0.1)
        await browser.close()
        return self.results

    def extract_page(self, response):
        selector = self.Selector(text=response)
        result = dict()
        result['play_addr'] = os.path.join("http://", selector.css("video::attr(src)").extract_first().lstrip("//"))
        result['title'] = selector.css("title::text").extract_first()
        result['vid'] = selector.css("meta").re_first("videoId=(\d{1,10})")
        result['cover'] = os.path.join("http://", selector.css("article img::attr(src)").extract_first().lstrip("//"))
        result['comment_count'] = selector.css(".floor-comments-count::text").extract_first()[1:-2]
        self.results.append(result)

    async def intercept_response(self, response):
        if "acs.m.taopiaopiao.com/h5/mtop.film.mtoptinyvideoapi.getvideo" in response.url:
            try:
                response_text = await response.text()
            except NetworkError:
                pass
            else:
                self.extract_xhr(response=response_text)

    def extract_xhr(self, response):
        response_json = json.loads(re.findall("\w.*?\(([\s|\S]*)\)", response)[0])
        video = jmespath.search("data.returnValue.video", response_json)
        result = {
            "author": jmespath.search("author", video),
            "avatar": os.path.join("http://gw.alicdn.com", jmespath.search("avatar", video)),
            "cover": os.path.join("http://gw.alicdn.com", jmespath.search("coverUrl", video)),
            "duration": jmespath.search("duration", video),
            "vid": jmespath.search("mediaId", video),
            "description": jmespath.search("media.desc", video),
            "view_count": jmespath.search("playCount", video),
            "play_addr": jmespath.search("playUrl.*", video)[-1],
            "title": jmespath.search("showName", video),
        }
        self.results.append(result)


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

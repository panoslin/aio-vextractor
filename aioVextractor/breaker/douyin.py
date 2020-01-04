#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from pyppeteer import launch
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
import jmespath
import time


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://v\.douyin\.com/[\w\d]{3,9}",  ## not avaliable, cause it overlap with extractor.douyin
        "http[s]?://www\.iesdouyin\.com/share/user/\d{5,25}",
    ]

    TEST_CASE = [
        "https://v.douyin.com/QXJURv",
        "https://v.douyin.com/QXJ6oG",
        "https://v.douyin.com/Q4E5R8/6725365523015581704",
        "https://www.iesdouyin.com/share/user/56035330573",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "douyin"
        self.results = []
        self.has_more = True
        self.playlist_url = None
        self.last_response = time.time()

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        self.playlist_url = webpage_url
        browser = await self.launch_browers()
        page = await browser.newPage()
        page.on('response', self.intercept_response)
        await page.goto(webpage_url)
        while self.has_more and time.time() - self.last_response <= 2:
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
        await browser.close()
        return self.results, False, {}

    async def intercept_response(self, response):
        resourceType = response.request.resourceType
        if resourceType in ['xhr'] and 'sec_uid=' in response.url:
            self.last_response = time.time()
            response_json = await response.json()
            self.extract(response=response_json)
            has_more = response_json['has_more']
            self.has_more = has_more

    def extract(self, response):
        aweme_list = response['aweme_list']
        for ele in aweme_list:
            try:
                duration = jmespath.search("video.duration", ele) // 1000
            except:
                duration = None
            self.results.append({
                "vid": ele['aweme_id'],
                "webpage_url": f"https://www.iesdouyin.com/share/video/{ele['aweme_id']}/?region=CN&mid={ele['aweme_id']}",
                "title": ele['desc'],
                "cover": jmespath.search("video.origin_cover.url_list[0]", ele),
                "play_addr": jmespath.search("video.download_addr.url_list[0]", ele),
                "duration": duration,
                "playlist_url": self.playlist_url,
                "from": self.from_,
            })


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2
        )
        pprint(res)

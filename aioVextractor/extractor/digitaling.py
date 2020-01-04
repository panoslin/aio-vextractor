#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry,
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.digitaling\.com/projects/\d{3,7}\.html",
        "http[s]?://www\.digitaling\.com/articles/\d{3,7}\.html",
        "http[s]?://m\.digitaling\.com/articles/\d{3,7}\.html",
        "http[s]?://m\.digitaling\.com/projects/\d{3,7}\.html",
    ]

    TEST_CASE = [
        "https://www.digitaling.com/projects/55684.html",
        "https://www.digitaling.com/projects/56636.html",
        "https://www.digitaling.com/articles/105167.html",
        "https://m.digitaling.com/projects/85861.html?plat=ios",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "digitaling"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url

        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )

        selector = Selector(text=text)
        youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
        tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
        urls = youku_urls + tencent_urls
        if not urls:
            return False

        results = await asyncio.gather(
            *[self.extract_iframe(
                iframe_url=iframe_url,
                session=session
            ) for iframe_url in urls])
        outputs = []
        for result in results:
            for ele in result:
                if ele:
                    outputs.append(ele)
        return outputs


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

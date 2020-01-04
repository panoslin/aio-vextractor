#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://socialbeta\.com/t/[\w-]*?\d{6,10}",
    ]

    TEST_CASE = [
        "https://socialbeta.com/t/jiafangyifang-news-20190226",
        "https://socialbeta.com/t/case-collection-overseas-ad-about-superbowl-20190224",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "socialbeta"

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
            *[
                self.extract_iframe(
                    iframe_url=iframe_url,
                    session=session
                ) for iframe_url in urls
            ])
        outputs = []
        for result in results:
            for ele in result:
                if ele:
                    # ele['from'] = self.from_
                    # ele['webpage_url'] = webpage_url
                    outputs.append(ele)
        return outputs


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

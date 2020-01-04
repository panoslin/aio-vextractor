#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import asyncio
from scrapy import Selector
from concurrent import futures  ## lib for multiprocessing and threading
import os
import re
import traceback
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.behance\.net/gallery/\d{1,15}/[\w-]{1,36}",
    ]

    TEST_CASE = [
        "https://www.behance.net/gallery/86216105/GOGORO-VIVA-LOGO-ANIMATION",
        "https://www.behance.net/gallery/76062469/Oreo-Stay-Playful?tracking_source=curated_galleries",
        "https://www.behance.net/gallery/86072525/I-am-Hunger-in-America-Feeding-America?tracking_source=curated_galleries",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "behance"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        cookies = {
            'gk_suid': '48143240',
            'gki': '%7B%22db_semaphore%22%3Afalse%2C%22live_featured_hero%22%3Afalse%7D',
            'bcp': 'e25d8bfb-7597-4118-a571-727307765213',
            'bcp_generated': '1572333735341',
            'ilo0': 'true',
        }

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Referer': re.findall(self.target_website[0], webpage_url)[0],
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            cookies=cookies
        )
        selector = Selector(text=response)
        iframe_src = selector.css('iframe::attr(src)').extract()
        return await self.breakdown(iframe_src=iframe_src)

    async def breakdown(self, iframe_src):
        def wrapper(url):
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                r = new_loop.run_until_complete(self.extract_info(webpage_url=url, collaborate=False))
                new_loop.close()
                return r
            except:
                traceback.print_exc()
                return False

        with futures.ThreadPoolExecutor(max_workers=min(10, os.cpu_count())) as executor:  ## set up processes
            executor.submit(wrapper)
            future_to_url = [executor.submit(wrapper, url=iframe) for iframe in iframe_src]
            results = []
            try:
                for f in futures.as_completed(future_to_url, timeout=max([len(iframe_src) * 3, 15])):
                    try:
                        result = f.result()
                        for ele in result:
                            if ele:
                                results.append(ele)
                    except:
                        traceback.print_exc()
                        continue
            except:
                traceback.print_exc()
                pass
            return results


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

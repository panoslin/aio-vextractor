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
        "http[s]?://creative\.adquan\.com/show/\d{3,7}",
        "http[s]?://www\.adquan\.com/post-\d-\d{3,7}\.html$",
        "http[s]?://mobile\.adquan\.com.*",
    ]

    TEST_CASE = [
        "https://creative.adquan.com/show/286788",
        "https://creative.adquan.com/show/286778",
        "http://www.adquan.com/post-2-49507.html",
        "http://creative.adquan.com/show/49469",
        "http://creative.adquan.com/show/49415",
        "https://mobile.adquan.com/creative/detail/288096",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "adquan"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url
        Cookie = 'Hm_lvt_b9772bb26f0ebb4e77be78655c6aba4e=1575882598; ' \
                 'acw_tc=65c86a0c15758827105424225eba98fda6d222f47abc0f66507ad18b9ee8b0; ' \
                 'area=eyJpdiI6IllPSEp0eXFZNG1RaExCQWhDbWI3WGc9PSIsInZhbHVlIjoiTm54UTcxYURYYmFGa01aYmhkRjQ1UT09IiwibWFjIjoiMGM2ZGRhZGQ5OTliZmIyNGQxMzJiMTQ3MTRkNWJmZDJiNjM1OTNiNTM5Nzc4N2QzZmUyMWQ1YjIxMDIzN2JjZSJ9; ' \
                 'Hm_lpvt_b9772bb26f0ebb4e77be78655c6aba4e=1576136108; ' \
                 'XSRF-TOKEN=eyJpdiI6IndrSVwvc25nc0tQV1UwRUgwbFVBVFpBPT0iLCJ2YWx1ZSI6IllFRGs5ODNsZk1IekNWdlFHeTZhRWxnbzRHWlR1OXlRaW9BajlDRVl4TE5pVHE5dXZMcUtoNjZcL3NBNmcxMjZYXC9cL3llSmgwK2JYc1g4Q1N2WExqd3Z3PT0iLCJtYWMiOiIyNDIwMTg2MjE0YzM0ODQ3ODU3MmRmOTFiYjBlOWNjMzRkYTM5M2I3MGUwNjg3ZDUzMWVjMzNlY2UwN2FiY2E2In0%3D; ' \
                 'laravel_session_production=eyJpdiI6Ik9zdldMVGZpb24wOG05VmNBWUNkcVE9PSIsInZhbHVlIjoid0xvWFg4VUpObTFYZjdOYXdCZnN1SHRWVHlMUzJ1eGlYYWRJaUZzMlM2R1lTTmxNcUdjODArS05tT083SG5lMU9SREU1XC9vdFJkVXVlVVBPWWlYbG5BPT0iLCJtYWMiOiI3ZjQ3NTQzOWE5MDNiM2MzODQ4MzYwOTNlNmE5MGNmM2NjY2YzZDI4YTY0YmM0Njg2Y2Q1OGUxNTU2YTE3YmE0In0%3D; ' \
                 'SERVERID=235be1bfd767f5d87ef3d43a3712e539|1576136108|1576136106; acw_sc__v2=5df1edcf5295e5cee219314bdb543364a9e9bb14'
        # Cookie = ''
        headers['Cookie'] = Cookie
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            # cookies=cookies
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
                    outputs.append(ele)
        return outputs


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(Extractor.TEST_CASE[-1])
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from scrapy import Selector
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from aioVextractor.utils import RequestRetry


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www.adforum.com/creative-work/ad/latest"
    ]

    TEST_CASE = [
        "https://www.adforum.com/creative-work/ad/latest",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "adforum"
        self.downloader = "ytd"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        # page = int(kwargs.pop("page", 1))
        headers = {
            'Cookie': 'FWKCountry=HK; '
                      '_ga=GA1.2.1760220707.1576203583; '
                      '_gid=GA1.2.1708855052.1576203583; '
                      '__gads=ID=4ea4d3f22ab8a7b0:T=1576203939:S=ALNI_MZMJGeMcpEO6nG-v_ZBbktAHExSNg; '
                      'XSRF-TOKEN=eyJpdiI6ImtleU0xZUx1NHZHa3prUlwveTFUR3BRPT0iLCJ2YWx1ZSI6Im5kbW5MZlI1Y1RNR2hnWnAzQU9Gb3VxNGZGcXRVekdnOVZzd28yS0pSTGRsSk5VQ05oRzZzQTVwNUhyQUczc3NQWEZGWWlaYlM1MVE4eDFZQk80ZUp3PT0iLCJtYWMiOiI1MjhiNmM0MGZkMzgxZTJiZDMwZDk4MDE2MTU4YzM2MjNhZDUwZmY4ZDI1OWMwYzBlZmY3MWI1NDJlYmM3YmVjIn0%3D; '
                      'adforum_session=eyJpdiI6ImlEUkJSeXp2akFkQXV4U0JJbnlRdlE9PSIsInZhbHVlIjoiT0tKVE0xaFJBdERwQ2YwU3dqbDFCdG1jQTFTQU1lVGRTOENtZW9PcUh3R0Z5aU9MeFFnMFh2ZVhjTkgxaTBodjBMd0Z3VnJ0a1c0TURNVlVHQTVHaGc9PSIsIm1hYyI6Ijg2NGJjY2FiNWE5YzcwMmQ2ZTVhY2ZlZWNiMGUwMjFiODM0YTczMDBjOWNjNDkyNmI1M2U1MDYyNDI0ZWE2ZjUifQ%3D%3D',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.108 Safari/537.36',
        }
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        selector = Selector(text=response)
        output = []
        http = 'https://www.adforum.com'
        for article in selector.css('div[class=b-latest-ads__item__header]'):
            ele = dict()
            ele['webpage_url'] = http + article.css(
                "div[class=b-latest-ads__item__header] a::attr(href)").extract_first()
            ele['vid'] = ele['webpage_url'].split('/')[6]
            ele['cover'] = article.css("div[class=b-latest-ads__item__header] a img::attr(data-src)").extract_first()
            ele['playlist_url'] = webpage_url
            ele['from'] = self.from_
            output.append(ele)
        return output, False, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
        )
        pprint(res)

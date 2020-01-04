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
        "http[s]?://www\.ispot\.tv/browse/.*"
    ]

    TEST_CASE = [
        "https://www.ispot.tv/browse/k/apparel-footwear-and-accessories",
        "https://www.ispot.tv/browse/Y/business-and-legal",
        "https://www.ispot.tv/browse/7/education",
        "https://www.ispot.tv/browse/A/electronics-and-communication",
        "https://www.ispot.tv/browse/d/food-and-beverage",
        "https://www.ispot.tv/browse/I/health-and-beauty",
        "https://www.ispot.tv/browse/o/home-and-real-estate",
        "https://www.ispot.tv/browse/Z/insurance",
        "https://www.ispot.tv/browse/w/life-and-entertainment",
        "https://www.ispot.tv/browse/q/politics-government-and-organizations",
        "https://www.ispot.tv/browse/7k/pharmaceutical-and-medical",
        "https://www.ispot.tv/browse/b/restaurants",
        "https://www.ispot.tv/browse/2/retail-stores",
        "https://www.ispot.tv/browse/5/travel",
        "https://www.ispot.tv/browse/L/vehicles",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "ispot"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        # page = int(kwargs.pop("page", 1))
        headers = {
            'Cookie':'PHPSESSID=297e1021f439744af6ae521d05653110; bhr=false; _ga=GA1.2.1821119186.1576138067; _gid=GA1.2.1130440238.1576138067; _fbp=fb.1.1576138069809.634925652; pt=v2:1cf949bf89854db69a2324dbb16113c23b9f00835c8c4e7baa5a518aa098efd2|5b39e378f8ba197fa5291975175236764da56891bbefd2ac0b968e04d84da4c0; visitor_id797423=39658931; visitor_id797423-hash=530ab073edff2abe8c580b5105feee8184384ff93735fd74b92e061507c634357e2096b074b8b167d7e972172662a8286cf86a64; _gat_UA-113623533-2=1; _gat_UA-31391020-1=1; da=1%7C0%7C2%7C6dba5094%7C9a40263b',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        selector = Selector(text=response)
        output = []
        http = 'https://www.ispot.tv'
        for article in selector.css('div[class=mb-0]'):
            ele = dict()
            ele['webpage_url'] = http + article.css("div[class=mb-0] a::attr(href)").extract_first()
            ele['vid'] = ele['webpage_url'].split('/')[4]
            ele['cover'] = article.css("div[class=mb-0] a img::attr(src)").extract_first()
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
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
        "http[s]?://www.tvcf.co.kr/\w{6}/List.asp"
    ]

    TEST_CASE = [
        "https://www.tvcf.co.kr/MovieK/List.asp",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "tvcf"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        headers = {
            'Cookie': 'ASPSESSIONIDSQRDCBBB=ONNFDEOADPCKKFPIBCPGBBGP',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        }
        params = (
            ('page', page),
            ('PumOne', ''),
            ('PumTwo', ''),
            ('Genre', ''),
            ('OrderBy', 'A.Fdate DESC, A.Title ASC, A.Code DESC'),
            ('TabIdx', 1),
            ('Date1', '1950-01-01'),
            ('Date2', '2019-12-31'),
        )
        response = await self.request(
            url=webpage_url,
            session=session,
            params=params,
            headers=headers,
        )

        selector = Selector(text=response)
        has_next = selector.css(f'a[onclick*=fnPageGo\({page + 1}\)]::text')
        output = []
        for article in selector.css('div[class=thumWrapfix]'):
            ele = dict()
            ele['webpage_url'] = article.css("div[class=thumWrapfix] a::attr(href)").extract_first()
            ele['vid'] = ele['webpage_url'].split('/')[-1]
            ele['cover'] = article.css("div[class=thumWrapfix] a div::attr(data-src)").extract_first()
            if ele['cover'] is None:
                ele['cover'] = article.css("div[class=thumWrapfix] a img::attr(src)").extract_first()
            ele['playlist_url'] = webpage_url
            ele['from'] = self.from_
            output.append(ele)
        return output, has_next, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
        )
        pprint(res)

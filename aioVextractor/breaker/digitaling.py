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
import re


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www\.digitaling\.com/\w{3}"
    ]

    TEST_CASE = [
        "https://www.digitaling.com/rss",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "digitaling"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        # page = int(kwargs.pop("page", 1))
        cookies = {
            'SERVERID': 'wrs04',
            '_ga': 'GA1.2.2044821304.1576230781',
        }

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.108 Safari/537.36',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            cookies=cookies
        )
        html_ = re.findall('<\?xml version="1.0"\?>([\s\S]*)', response)[0]
        items_ = re.findall('<item>([\S\s]*?)</item>', html_)
        output = []
        for item_ in items_:
            title = re.findall('<title><!\[CDATA\[ ([\S\s]*?)]]></title>', item_)[0]
            link = re.findall('<link><!\[CDATA\[ ([\S\s]*?)]]></link>', item_)[0]
            description = re.findall('<description><!\[CDATA\[ ([\S\s]*?)]]></description>', item_)[0]
            selector = Selector(text=description)
            cover = selector.css('img::attr(src)').extract_first()
            vid = link.split('/')[4].strip('.html')
            if '招聘频道' in title:
                continue
            else:
                item = {
                    'title': title,
                    'webpage_url': link,
                    'cover': cover,
                    'vid': vid,
                    'playlist_url': webpage_url,
                    'from': self.from_,
                }
                output.append(item)
        return output, False, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
        )
        pprint(res)

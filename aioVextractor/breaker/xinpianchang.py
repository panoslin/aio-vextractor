#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from urllib.parse import unquote
import html
import emoji
import traceback
from scrapy import Selector
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from aioVextractor.utils import RequestRetry


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www\.xinpianchang\.com/u\d{5,10}",
    ]

    TEST_CASE = [
        "https://www.xinpianchang.com/u10014261?from=userList",
        "https://www.xinpianchang.com/u10029931?from=userList",
        "https://www.xinpianchang.com/u10002513?from=userList",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "xinpianchang"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        url = "https://www.xinpianchang.com/index.php"
        xinpianchang_user_id = webpage_url.split('?')[0].split('/u')[-1]
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Origin'] = "https://www.xinpianchang.com"
        headers['Referer'] = webpage_url
        headers['X-Requested-With'] = "XMLHttpRequest"
        params = {"app": "user",
                  "ac": "space",
                  "ajax": "1",
                  "id": xinpianchang_user_id,
                  "d": "1",
                  "sort": "pick",
                  "cateid": "0",
                  "audit": "1",
                  "is_private": "0",
                  "page": page}
        clips = await self.request(
            url=url,
            session=session,
            headers=headers,
            params=params,
            method="post",
        )
        results = await self.extract_user_pageing_api(ResText=clips, webpage_url=webpage_url)
        return results

    async def extract_user_pageing_api(self, ResText, webpage_url):
        try:
            selector = Selector(text=ResText)
        except TypeError:
            return None
        output = []
        for article in selector.css("li[data-articleid]"):
            ele = dict()
            ele['vid'] = article.css('::attr(data-articleid)').extract_first()
            ele['webpage_url'] = f"https://www.xinpianchang.com/a{ele['vid']}?from=UserProfile"
            ele['cover'] = article.css('img[class*="lazy-img"]::attr(_src)').extract_first()
            ele['upload_ts'] = self.string2timestamp(
                string=article.css('.video-hover-con p[class*="fs_12"]::text').extract_first(),
                format='%Y-%m-%d 发布'
            )
            # ele['duration'] = self.format_duration(article.css('.duration::text').extract_first())
            ele['duration'] = self.string2duration(
                string=article.css('.duration::text').extract_first(),
                format="%M' %S''"
            )
            ele['description'] = self.format_desc(article.css('.desc::text').extract_first())
            ele['playlist_url'] = webpage_url
            ele['title'] = self.format_desc(article.css('.video-con-top p::text').extract_first())
            ele['category'] = self.format_category(article.css('.new-cate .c_b_9 ::text').extract())
            ele['view_count'] = self.format_count(article.css('.icon-play-volume::text').extract_first())
            ele['like_count'] = self.format_count(article.css('.icon-like::text').extract_first())
            ele['role'] = article.css('.user-info .role::text').extract_first()
            ele['from'] = self.from_
            output.append(ele)
        else:
            has_more = selector.css("li[data-more]::attr(data-more)").extract_first()
            return output, has_more, {}

    @staticmethod
    def format_category(category):
        """
        input: ['\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t系列短视频\t\t\t\t\t\t\t', '\n\t\t\t\t\t\t\t纪录 - 亲情\t\t\t\t\t\t\t']
        """
        return ",".join(list(map(lambda x: x.strip(), category))) if category else None

    @staticmethod
    def format_desc(desc):
        try:
            return emoji.demojize(html.unescape(unquote(desc)))
        except:
            return desc

    @staticmethod
    def format_count(num):
        try:
            if 'w' in num:
                return str(int(float(num.replace('w', '')) * 10000))
            else:
                return num
        except:
            traceback.print_exc()
            return num


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[0],
        )
        pprint(res)

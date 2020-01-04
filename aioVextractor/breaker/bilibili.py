#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import re
import traceback
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "https://space\.bilibili\.com/\d{5,10}",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://space.bilibili.com/29296192/video",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "bilibili"

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'{webpage_url}/video?tid=0&page={page-1}&keyword=&order=pubdate'
            if page > 1
            else f'{webpage_url}/video?tid=0&page=1&keyword=&order=pubdate',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
        }
        mid = re.findall("https://space\.bilibili\.com/(\d{5,10})", webpage_url)[0]
        params = (
            ('mid', mid),
            ('pagesize', '30'),
            ('tid', '0'),
            ('page', str(page)),
            ('keyword', ''),
            ('order', 'pubdate'),
        )
        api = 'https://space.bilibili.com/ajax/member/getSubmitVideos'
        response = await self.request(
            url=api,
            headers=headers,
            session=session,
            params=params,
            response_type="json"
        )

        results = self.extract(response=response, page=page, playlist_url=webpage_url)
        return results

    def extract(self, response, page, playlist_url):
        results = []
        vlist = jmespath.search("data.vlist", response)
        max_page = response['data']['pages']
        has_more = True if page < max_page else False
        for ele in vlist:
            try:
                results.append({
                    "comment_count": ele['comment'],
                    "view_count": ele['play'],
                    "cover": "http://" + ele['pic'].strip('//'),
                    "description": ele['description'],
                    "title": ele['title'],
                    "author": ele['author'],
                    "author_id": ele['mid'],
                    "upload_ts": ele['created'],
                    "vid": ele['aid'],
                    "duration": self.cal_duration(ele['length']),
                    "from": "bilibili",
                    "playlist_url": playlist_url,
                    "webpage_url": f'https://www.bilibili.com/video/av{ele["aid"]}',
                })
            except:
                traceback.print_exc()
                continue
        else:
            return results, has_more, {}

    @staticmethod
    def cal_duration(raw_duration_string):
        regex = re.compile("(\d{1,3}):?")
        _duration = regex.findall(raw_duration_string)
        duration = 0
        for num, i in enumerate(_duration[::-1]):
            duration += int(i) * (60 ** num)
        return duration


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[0],
            # page=2
        )
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import jmespath
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www.tvcbook.com/",
    ]

    TEST_CASE = [
        "https://www.tvcbook.com/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "tvcbook"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        results = []
        headers = {
            'authority': 'api.tvcbook.com',
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://www.tvcbook.com',
            'user-agent': self.random_ua(),
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.tvcbook.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

        params = (
            ('r', '1'),
            ('sort', 'recommend_desc'),
            ('per-page', '24'),
            ('expand', 'credits_total,credits_list,is_verified,social'),
        )
        api = 'https://api.tvcbook.com/r/top'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            response_type='json'
        )
        items = jmespath.search('data.data.items', response)
        for item in items:
            vid = jmespath.search('video_id', item)
            code = jmespath.search('code', item)
            result = {
                'vid': vid,
                'title': jmespath.search('title', item),
                'cover': jmespath.search('cover_url', item),
                'author': jmespath.search('credits_list[0].creator_name', item),
                'author_id': jmespath.search('credits_list[0].user_id', item),
                'webpage_url': f'https://www.tvcbook.com/showVideo.html?vid={vid}&code={code}',
                'playlist_url': webpage_url,
                'from': self.from_,
            }
            results.append(result)
        return results, False, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)

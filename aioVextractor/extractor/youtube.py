#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
from scrapy import Selector
import asyncio
import platform
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.youtube\.com/watch\?v=[\w-]{5,15}",
        "http[s]?://youtu\.be/[\w-]{5,15}",
        "http[s]?://m\.youtube\.com/watch\?.*?v=[\w-]{5,15}",
    ]

    TEST_CASE = [
        "https://www.youtube.com/watch?v=tofSaLB9kwE",
        "https://www.youtube.com/watch?v=pgN-vvVVxMA",
        "https://www.youtube.com/watch?v=iAeYPfrXwk4",
        "https://www.youtube.com/watch?v=jDO2YPGv9fw&list=PLNHZSfaJJc25zChky2JaM99ba8I2bVUza&index=15&t=0s",
        "https://www.youtube.com/watch?v=JGwWNGJdvx8&list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs&index=28&t=0s",
        "https://youtu.be/NJbWAMCM1P4",
        "https://www.youtube.com/watch?v=D2LsdT-hldY",
        "https://m.youtube.com/watch?v=EtH9Yllzjcc&feature=youtu.be",
        "https://m.youtube.com/watch?feature=youtu.be&v=YG-VJU444ac",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "youtube"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        gather_results = await asyncio.gather(*[
            self.extract_info(webpage_url=webpage_url),
            self.extract_author(webpage_url=webpage_url, session=session)
        ])
        if isinstance(gather_results[0], list):
            results = [self.merge_dicts(ele, gather_results[1]) for ele in gather_results[0]]
            return results
        else:
            return self.merge_dicts(*gather_results)

    @RequestRetry(
        default_other_exception_return={}
    )
    async def extract_author(self, webpage_url, session):
        headers = {'authority': 'www.youtube.com',
                   'upgrade-insecure-requests': '1',
                   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   }
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )
        selector = Selector(text=text)
        try:
            ytInitialData = json.loads(json.
                                       loads(selector.
                                             css('script').
                                             re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
        except TypeError:
            ytInitialData = json.loads(selector.css('script').re_first(
                'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
        author_avatar = jmespath.search('contents.'
                                        'twoColumnWatchNextResults.'
                                        'results.'
                                        'results.'
                                        'contents[1].'
                                        'videoSecondaryInfoRenderer.'
                                        'owner.'
                                        'videoOwnerRenderer.'
                                        'thumbnail.'
                                        'thumbnails[-1].'
                                        'url',
                                        ytInitialData)

        author_avatar = 'http:' + author_avatar if (author_avatar and author_avatar.startswith('//')) else author_avatar
        return {
            "author_avatar": author_avatar,
        }


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        ress = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(ress)

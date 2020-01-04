#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import asyncio
from aioVextractor.utils.user_agent import safari
from random import choice
from scrapy import Selector
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://vimeo\.com/\d{7,18}$"
    ]

    TEST_CASE = [
        "https://vimeo.com/281493330",
        "https://vimeo.com/344361560",
        "https://vimeo.com/5721553",
        "https://vimeo.com/368525290",
        "https://vimeo.com/372477622",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "vimeo"

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
            results = self.merge_dicts(*gather_results)
        for ele in results:
            ele['cover'] = self.check_cover(ele['cover'])
        return results


    @RequestRetry(
        default_other_exception_return={}
    )
    async def extract_author(self, webpage_url, session):
        headers = self.general_headers(user_agent=choice(safari))
        headers['Referer'] = 'https://vimeo.com/search?q=alita'
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        regex = '"portrait":\{"src":".*?",\s*"src_2x":"(.*?)"\},'
        selector = Selector(text=text)
        clip_page_config = selector.css('script').re_first(regex)
        avatar = clip_page_config.replace('\\/', '/')
        return {"author_avatar": avatar,
                # 'from': self.from_
                }


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

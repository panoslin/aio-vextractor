#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from urllib.parse import urlparse
import jmespath
from scrapy.selector import Selector
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
        "http[s]?://www\.vmovier\.com/\d{2,8}",
    ]

    TEST_CASE = [
        ## xpc player:
        "https://www.vmovier.com/56000?from=index_new_img",
        ## youku player:
        "https://www.vmovier.com/56052?from=index_new_title",
        "https://www.vmovier.com/55952?from=index_new_img",
        "https://www.vmovier.com/55108",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "vmovier"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = 'http://creative.adquan.com/'
        response_text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        selector = Selector(text=response_text)
        xinpianchang_url = selector.css('.post-title a::attr(href)').extract()
        openapi_url = selector.css('iframe[src*=openapi]::attr(src)').extract()
        youku_url = list(map(lambda x: f'https://v.youku.com/v_show/id_{x}',
                             selector.css('script::text').re("vid: '([\s|\S]*?)'")))
        urls = xinpianchang_url + openapi_url + youku_url

        if not urls:
            return False

        results = await asyncio.gather(
            *[
                self.allocate_url(url=url_,
                                  session=session,
                                  referer=webpage_url,
                                  selector=selector)
                for url_ in urls
            ])

        outputs = []
        for result in results:
            for ele in result:
                if ele:
                    outputs.append(ele)

        return outputs

    async def allocate_url(self, url, session, referer=None, selector=None):
        if 'openapi' in url:
            return await self.extract_openapi_info(selector=selector,
                                                   player_address=url,
                                                   referer=referer,
                                                   session=session)
        else:
            return await self.extract_iframe(iframe_url=url, session=session)

    @RequestRetry
    async def extract_openapi_info(self, selector, player_address, referer, session):
        result = dict()
        result['vid'] = urlparse(player_address).path.split('/')[2]
        result['author'] = selector.css('.author::text').extract_first()
        result['title'] = selector.css('meta[name*=application-name]::attr(content)').extract_first()
        result['category'] = selector.css('.channel a::attr(title) ').extract_first()
        result['description'] = selector.css('meta[name*=description]::attr(content)').extract_first()
        tag = selector.css('meta[name*=keywords]::attr(content)').extract_first()
        result['tag'] = tag.split(',') if tag else None
        headers = self.general_headers(user_agent=self.random_ua())
        headers['referer'] = referer
        headers['authority'] = 'openapi-vtom.vmovier.com'
        player_response_text = await self.request(
            url=player_address,
            session=session,
            headers=headers,
        )
        player_selector = Selector(text=player_response_text)
        result['cover'] = player_selector.css('#xpc_video::attr(poster)').extract_first()
        video = json.loads(player_selector.css('script').re_first('var origins = (\[[\s|\S]*?\])'))
        duration, result['play_addr'] = jmespath.search('max_by(@, &filesize).[duration, url]', video)
        result['duration'] = int(duration / 1000) if duration else None
        return [result]


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

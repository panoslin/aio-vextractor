#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/28/19
# IDE: PyCharm

import jmespath
from scrapy.selector import Selector
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.hellorf\.com/video.show/\d{5,10}",
    ]

    TEST_CASE = [
        "https://www.hellorf.com/video/show/15148543",
        "https://www.hellorf.com/video/show/11995691",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "hellorf"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        async with session.get(webpage_url, headers=self.general_headers(self.random_ua())) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=response_text)
            result = dict()
            video_json = json.loads(selector.css('#__NEXT_DATA__::text').re_first('([\s|\S]*)'))
            detail = jmespath.search("props.pageProps.initialProps.detail", video_json)
            result['author'] = jmespath.search('contributor.display_name', detail)
            result['play_addr'] = jmespath.search('video.preview_mp4_url', detail)
            result['title'] = jmespath.search('video.description', detail)
            result['vid'] = jmespath.search('video.id', detail)
            video_category = jmespath.search('video.categories[].name', detail)
            result['category'] = ','.join(video_category)
            result['cover'] = jmespath.search('video.preview_jpg_url', detail)
            result['duration'] = jmespath.search('video.duration', detail)
            result['tag'] = jmespath.search('video.keywords', detail)
            # result['from'] = self.from_
            # result['webpage_url'] = webpage_url
            return result

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/07/19
# IDE: PyCharm

import jmespath
import platform
from scrapy import Selector
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
        "http[s]?://www\.pinterest\.com/pin/\d{15,23}",
        "http[s]?://www\.pinterest\.com/pin/.*",
    ]

    TEST_CASE = [
        "https://www.pinterest.com/pin/457256168416688731",
        "https://www.pinterest.com/pin/ARcZcYFNPiz50mXPWWpHt9G6aU2goEVhi-Jvtl8A2z-ptXYirv0z8bM/",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "pinterest"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        headers["Host"] = "www.pinterest.com"

        html = await self.request(
            url=webpage_url,
            session=session,
            ssl=False,
            headers=headers
        )
        selector = Selector(text=html)
        jsonstr = selector.css("#initial-state::text").extract_first()
        if not jsonstr:
            return None
        jsondata = json.loads(jsonstr)
        video = jmespath.search("resourceResponses[0].response.data", jsondata)
        videos = jmespath.search("videos", video)
        try:
            duration = jmespath.search("video_list.*.duration", videos)[0] // 1000
        except:
            duration = None
        result = {
            # "from": self.from_,
            "vid": video['id'],
            # "webpage_url": f"https://www.pinterest.com/pin/{video['id']}",
            "playlist_url": webpage_url,
            "cover": jmespath.search("max_by(images.*, &width).url", video),
            "title": jmespath.search("title", video),
            "duration": duration,
            "play_addr": jmespath.search("max_by(video_list.*, &width).url", videos),
            "width": jmespath.search("max_by(video_list.*, &width).width", videos),
            "height": jmespath.search("max_by(video_list.*, &height).height", videos),
            "description": jmespath.search("rich_summary.display_description", video),
            "ad_link": jmespath.search("rich_summary.url", video),
            "author": jmespath.search("pinner.username", video),
            "author_id": jmespath.search("pinner.id", video),
            "avatar": jmespath.search("pinner.image_large_url", video),
            "author_url": webpage_url,
            "comment_count": jmespath.search("comment_count", video),
        }
        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

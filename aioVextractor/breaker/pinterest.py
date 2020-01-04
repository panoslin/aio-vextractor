#!/usr/bin/env python
# -*- coding: utf-8 -*-
# IDE: PyCharm

import traceback
import time
import re
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
import json


class Breaker(BaseBreaker):
    target_website = [
        "http[s]://www\.pinterest.com/[\w-]{5,36}/video_pins/",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://www.pinterest.com/luvbridal/video_pins/",
        "https://www.pinterest.com/viralanimalfun/video_pins/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "pinterest"

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        user_name = re.findall("http[s]://www\.pinterest.com/([\w-]{5,36})/video_pins/", webpage_url)[0]
        source_url = f"/{user_name}/video_pins"
        page = int(kwargs.pop("page", 1))
        if page > 1:
            data = json.dumps(kwargs)
        else:
            data = '{"options":{"isPrefetch":false,"exclude_add_pin_rep":true,"username":"' \
                   + user_name \
                   + '","field_set_key":"grid_item"},"context":{}}'

        jsondata = await self.request(
            url='https://www.pinterest.com/_ngjs/resource/UserVideoPinsFeedResource/get/',
            session=session,
            ssl=False,
            params=(
                (f'source_url{source_url}', ''),
                ('data', data),
                ('_', f'{str(int(time.time() * 1000))}\' -H authority:'),
            ),
            response_type="json"
        )
        return self.extract(response_json=jsondata, webpage_url=webpage_url)

    def extract(self, response_json, webpage_url):
        video_data = jmespath.search("resource_response.data", response_json)
        results = []
        for video in video_data:
            videos = video.get("videos")

            try:
                duration = jmespath.search("video_list.*.duration", videos)[0] // 1000
            except:
                duration = None
            try:
                result = {
                    "from": self.from_,
                    "vid": video['id'],
                    "webpage_url": f"https://www.pinterest.com/pin/{video['id']}",
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
                results.append(result)
            except:
                traceback.print_exc()
                continue

        bookmarks = jmespath.search("resource.options.bookmarks", response_json)
        resource = jmespath.search("resource.options", response_json)
        has_next = False if not bookmarks or bookmarks[0] == '-end-' else True
        params = {"options": resource, "context": {}} if has_next else {}
        return results, has_next, params


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            params={'context': {},
                    'options': {'bookmarks': [
                        'Pz9mZmZmZmZmZmEyM2U3YWZmMGI1YjQwMTAwMGU2ZDc1NXw5NTc0YTY4ZDAzZmU2Zjc0MmVmMWI3Y2Q2NmI1YWQxMmMwNTBhMTEzYzE4ZWNjMjMzN2ZmYjU4OWRhOTZkYTdmfE5FV3w='],
                        'exclude_add_pin_rep': True,
                        'field_set_key': 'grid_item',
                        'isPrefetch': False,
                        'username': 'viralanimalfun'},
                    'page': 2
                    }
        )
        pprint(res)

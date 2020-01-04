#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import re, json, time
import jmespath

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://carben\.me/video/\d{1,6}",
    ]

    TEST_CASE = [
        "https://carben.me/video/9049",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "carben"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):

        text = await self.request(
            url=webpage_url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua())
        )
        jsondata = json.loads(re.findall("window.__NUXT__=(.*?);<", text)[0])
        video = jmespath.search("data[0].feeddata.video", jsondata)
        try:
            width, height = re.compile('_(\d{3,4})x(\d{3,4})\.').findall(jmespath.search('qualities[0].path', video))[0]
        except:
            width = height = None
        if jmespath.search('author.id', video):
            author_url = "https://carben.me/user/" + str(jmespath.search('author.id', video))
        else:
            author_url=None
        result = {
            "cover": video['cover'],
            "vid": video['id'],
            "description": jmespath.search("description", video),
            "tag": jmespath.search("tags", video),
            "title": jmespath.search("title", video),
            "duration": jmespath.search("duration", video),
            "share_count": jmespath.search("shareCount", video),
            "recommend": jmespath.search("recommend", video),
            "view_count": jmespath.search("playCount", video),
            "like_count": jmespath.search("likeCount", video),
            "collect_count": jmespath.search("collectionCount", video),
            "comment_count": jmespath.search("replyCount", video),
            "author": jmespath.search("author.name", video),
            "author_avatar": jmespath.search("author.icon", video),
            "author_id": jmespath.search("data[0].feeddata.user.id", jsondata),
            "play_addr": jmespath.search('qualities[0].path', video),
            "width": width,
            "height": height,
            "author_url": author_url,
            "upload_ts": int(time.mktime(time.strptime(video.get("published_at"), "%Y-%m-%d %H:%M:%S"))),

        }

        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

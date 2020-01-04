#!/usr/bin/env python
# -*- coding: utf-8 -*-
# IDE: PyCharm

import jmespath
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

class Breaker(BaseBreaker):
    target_website = [
        "http[s]://www\.instagram\.com/[\w\.-]{1,50}",
        "http[s]://instagram\.com/[\w\.-]{1,50}",
    ]

    # downloader = 'ytd'

    TEST_CASE = [
        "https://www.instagram.com/funnymike/",
        "https://www.instagram.com/filmmkrs?igshid=186z6y04dov3y",
        "https://www.instagram.com/cchannel_beauty/",
        "https://www.instagram.com/psg/",
        "https://www.instagram.com/fashion.upk/",
        "https://www.instagram.com/hano.gram",
        "https://instagram.com/renopedia?igshid=dpu27sj4wxok",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "instagram"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        if page > 1:
            results = await self.GetOther(kwargs, session, webpage_url)
            return results
        else:
            results = await self.GetFirst(webpage_url, session)
            return results

    @RequestRetry
    async def GetOther(self, params, session, playlist_url):
        tagurl = f"https://www.instagram.com/graphql/query/?query_hash={params['query_hash']}"
        urlp = '{' + '"id":"{}","first":12,"after":"{}"'.format(params['id'], params['end_cursor']) + '}'
        tagurl = f"{tagurl}&variables={urlp}"
        results = []
        html = await self.request(
            url=tagurl,
            session=session,
            ssl=False
        )
        jsondata = json.loads(html)
        user = jmespath.search("data.user", jsondata)
        if not user:
            return None
        edges = jmespath.search("edge_owner_to_timeline_media.edges", user)
        has_next = jmespath.search("edge_owner_to_timeline_media.page_info.has_next_page", user)
        params = {
            "query_hash": "f2405b236d85e8296cf30347c9f08c2a",
            "id": params['id'],
            "first": 12,
            "end_cursor": jmespath.search("edge_owner_to_timeline_media.page_info.end_cursor", user),
        } if has_next else {}
        for video in edges:
            node = jmespath.search("node", video)
            if node.get("is_video"):
                result = {
                    "duration": jmespath.search("video_duration", node),
                    "like_count": jmespath.search("edge_liked_by.count", node),
                    "comment_count": jmespath.search("edge_media_to_comment.count", node),
                    "description": jmespath.search("edge_media_to_caption.edges[0].node.text", node),
                    "from": self.from_,
                    "cover": node['display_url'],
                    "author": jmespath.search("owner.username", node),
                    "author_id": jmespath.search("owner.id", node),
                    "webpage_url": f'https://www.instagram.com/p/{jmespath.search("shortcode", node)}/',
                    "vid": jmespath.search("shortcode", node),
                    "view_count": jmespath.search("video_view_count", node),
                    "playlist_url": playlist_url,
                }
                results.append(result)
        return results, has_next, params

    @RequestRetry
    async def GetFirst(self, webpage_url, session):
        results = []
        webpage_url = webpage_url.split("?")[0] + '?__a=1'
        html = await self.request(
            url=webpage_url,
            session=session,
            ssl=False
        )
        jsondata = json.loads(html)
        user = jmespath.search("graphql.user", jsondata)
        if not user:
            return None
        edges = jmespath.search("edge_owner_to_timeline_media.edges", user)
        has_next = jmespath.search("edge_owner_to_timeline_media.page_info.has_next_page", user)
        params = {
            "query_hash": "f2405b236d85e8296cf30347c9f08c2a",
            "id": user['id'],
            "first": 12,
            "end_cursor": jmespath.search("edge_owner_to_timeline_media.page_info.end_cursor", user),
        } if has_next else {}
        for video in edges:
            node = jmespath.search("node", video)
            if node.get("is_video"):
                result = {
                    "duration": jmespath.search("video_duration", node),
                    "like_count": jmespath.search("edge_liked_by.count", node),
                    "comment_count": jmespath.search("edge_media_to_comment.count", node),
                    "description": jmespath.search("edge_media_to_caption.edges[0].node.text", node),
                    "from": self.from_,
                    "cover": node['display_url'],
                    "author": jmespath.search("owner.username", node),
                    "author_id": jmespath.search("owner.id", node),
                    "webpage_url": f'https://www.instagram.com/p/{jmespath.search("shortcode", node)}/',
                    "vid": jmespath.search("shortcode", node),
                    "view_count": jmespath.search("video_view_count", node),
                    "playlist_url": webpage_url.replace("?__a=1", ""),
                }
                results.append(result)
        return results, has_next, params


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # params={
            #     'end_cursor': 'QVFDRWVWQ2xMbEhqUko5YkdLR0Jib2JhbUQwcTBiZEtCa3Y1by14amZEam5iNGxqUUZnOEFWUUhPZ1pFaTdfMHhRbFJlNGRVOFRrRy1tNnczY1g5WkFfaQ==',
            #     'first': 12,
            #     'id': '3679812611',
            #     'query_hash': 'f2405b236d85e8296cf30347c9f08c2a'}
        )
        pprint(res)

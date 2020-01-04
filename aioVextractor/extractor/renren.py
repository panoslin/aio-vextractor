#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

import re
import asyncio
import jmespath
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://mobile\.rr\.tv/mission/#/share/video\?id=\d{3,7}",
    ]

    TEST_CASE = [
        "https://mobile.rr.tv/mission/#/share/video?id=1879897",
        "https://mobile.rr.tv/mission/#/share/video?id=1879530",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "renren"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        try:
            vid = re.compile('id=(\d*)').findall(webpage_url)[0]
        except IndexError:
            return False
        else:
            result = await asyncio.gather(self.extract_playLink(vid=vid, session=session),
                                          self.extract(vid=vid, session=session))
            if all(result):
                result_playLink, result_info = result
                return {**result_playLink, **result_info}
            else:
                return False

    @RequestRetry
    async def extract_playLink(self, vid, session):
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://mobile.rr.tv/mission/',
                   'Origin': 'https://mobile.rr.tv',
                   'clientType': 'web',
                   'User-Agent': self.random_ua(),
                   'token': 'undefined',
                   'clientVersion': 'undefined'}
        params = {'videoId': vid}
        ResJson = await self.request(
            url='https://api.rr.tv/v3plus/video/getVideoPlayLinkByVideoId',
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        if ResJson['code'] != '0000':
            return False
        elif not ResJson['data']['playLink']:
            return False
        else:
            return {'vid': vid, 'play_addr': ResJson['data']['playLink']}

    @RequestRetry
    async def extract(self, vid, session):
        headers = {'Origin': 'https://mobile.rr.tv',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
                   'User-Agent': self.random_ua(),
                   'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://mobile.rr.tv/mission/',
                   'clientVersion': 'undefined',
                   'Connection': 'keep-alive',
                   'token': 'undefined',
                   'clientType': 'web'}
        params = {'videoId': vid}
        VideoDetail = await self.request(
            url='https://api.rr.tv/v3plus/video/detail',
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        result = dict()
        # result['webpage_url'] = webpage_url
        # result['from'] = self.from_
        videoDetailView = jmespath.search('data.videoDetailView', VideoDetail)
        result['author'] = jmespath.search('author.nickName', videoDetailView)
        result['avatar'] = jmespath.search('author.headImgUrl', videoDetailView)
        result['role'] = jmespath.search('author.roleInfo', videoDetailView)
        result['author_videoNum'] = jmespath.search('author.videoCount', videoDetailView)
        result['title'] = jmespath.search('title', videoDetailView)
        result['category'] = jmespath.search('type', videoDetailView)
        result['cover'] = jmespath.search('cover', videoDetailView)
        result['description'] = jmespath.search('brief', videoDetailView)
        result['tag'] = jmespath.search('tagList[].name', videoDetailView)
        video_duration = jmespath.search('duration', videoDetailView)
        result['duration'] = self.cal_duration(video_duration) if video_duration else None
        return result

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

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

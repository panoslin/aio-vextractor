#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
import traceback
import re
import asyncio
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
        "http[s]?://www\.bilibili\.com/video/av\d{4,9}",
        "http[s]?://m\.bilibili\.com/video/av\d{4,9}",
        "http[s]?://b23\.tv/av\d{1,10}",
        "http[s]?://t\.cn/\w{1,10}",
    ]

    TEST_CASE = [
        "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
        "https://b23.tv/av68290345",
        "https://m.bilibili.com/video/av75755418?spm_id_from=333.400.b_766964656f5f30.1",
        "http://t.cn/R3LCQFl",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "bilibili"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        if re.match("http[s]?://t\.cn/\w{1,10}", webpage_url):
            response = await self.request(
                url=webpage_url,
                session=session,
                headers=self.general_headers(user_agent=self.random_ua()),
                allow_redirects=False,
                response_type="raw",
            )
            webpage_url = response.headers['Location']

        result = {'vid': re.findall("/av(\d{5,20})", webpage_url)[0]}
        gather_results = await asyncio.gather(*[
            self.extract_info(webpage_url=webpage_url),
            self.extract_video(result=result, session=session)
        ])
        if all(gather_results):
            if isinstance(gather_results[0], list):
                results = [self.merge_dicts(ele, gather_results[1]) for ele in gather_results[0]]
                return results
            else:
                return self.merge_dicts(*gather_results)
        else:
            return False

    @RequestRetry
    async def extract_video(self, result, session):
        user_agent = self.random_ua()
        headers = self.general_headers(user_agent=user_agent)
        headers['Referer'] = 'https://m.bilibili.com/index.html'
        av_url = f'https://m.bilibili.com/video/av{result["vid"]}.html'
        html = await self.request(
            url=av_url,
            session=session,
            headers=headers
        )
        jsonstr = re.findall("window.__INITIAL_STATE__\s?=\s?(.*?)};", html)  # 提取json数据 为保证容错 用 }; 来标识
        if jsonstr:
            jsonstr = jsonstr[0] + '}'
        else:
            return False
        try:
            jsondata = json.loads(jsonstr)
            result['comment_count'] = jmespath.search('comment.count', jsondata)
            result['tag'] = jmespath.search('tags[].tag_name', jsondata)
            result['author_avatar'] = jmespath.search('upData.face', jsondata)
            result['author_description'] = jmespath.search('upData.description', jsondata)
            result['author_birthday'] = jmespath.search('upData.birthday', jsondata)
            result['author_follwer_count'] = jmespath.search('upData.fans', jsondata)
            result['author_follwing_count'] = jmespath.search('upData.friend', jsondata)
            result['author_id'] = jmespath.search('upData.mid', jsondata)
            result['author'] = jmespath.search('upData.name', jsondata)
            result['gender'] = jmespath.search('upData.sex', jsondata)
            result['author_sign'] = jmespath.search('upData.sign', jsondata)
            result['upload_ts'] = jmespath.search('videoData.ctime', jsondata)
            result['description'] = jmespath.search('videoData.desc', jsondata)
            result['duration'] = jmespath.search('videoData.duration', jsondata)
            result['title'] = jmespath.search('videoData.title', jsondata)
            return result
        except:
            traceback.print_exc()
            return False


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import re
import random
from urllib.parse import urlparse
import binascii
import base64
import jmespath
import execjs
import platform
import os
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import time

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://m\.toutiaoimg\.com/a\d{10,36}",
        "http[s]?://m\.toutiaocdn\.com/a\d{10,36}",
        "http[s]?://m\.toutiaoimg\.cn/group/\d{10,36}",
        "http[s]?://m\.toutiaocdn\.net/a\d{10,36}",
        "http[s]?://m\.toutiaocdn\.com/i\d{10,36}",
        "http[s]?://m\.toutiaoimg\.com/group/\d{10,36}",
        "http[s]?://m\.ixigua\.com/i\d{10,36}",
        "http[s]?://m\.toutiao\.com/i\d{10,36}",
    ]

    TEST_CASE = [
        "https://m.toutiaoimg.com/a6731923698707595790/?app=news_article&is_hit_share_recommend=0",
        "雨桐的电影: 气质这一块没输过！https://m.toutiaoimg.cn/group/6747521740714429707/?app=news_article&timestamp=1572243832",
        "https://m.toutiaocdn.com/a6752189114830815757/?app=news_article&is_hit_share_recommend=0",
        "https://m.toutiaocdn.net/a6752504513917092359/?app=news_article&is_hit_share_recommend=0",
        "https://m.toutiaocdn.com/i6752291249207640590/?app=news_article&timestamp=1572147617&req_id=201910271140170100140481310BDEA279&group_id=6752291249207640590&wxshare_count=20&tt_from=weixin_moments&utm_source=weixin_moments&utm_medium=toutiao_android&utm_campaign=client_share&share_type=original&pbid=6751721020236875277&from=singlemessage&isappinstalled=0",
        "https://m.toutiaoimg.com/group/6739755269032509966/?app=news_article_lite&timestamp=1572244151&req_id=20191028142911010011048231030168A8&group_id=6739755269032509966",
        "https://m.toutiaoimg.com/group/6758768712024588295/?app=news_article&timestamp=1573886933",
        "来看看@光头强捡到冒菜的视频https://m.toutiaoimg.cn/group/6760527483755449611/?app=news_article&timestamp=1574258101",
        "https://m.toutiaocdn.net/a6761067781120066062/?app=news_article&is_hit_share_recommend=0",
        "https://m.ixigua.com/i6761248990626316811/?channel=video",
        "https://m.toutiao.com/i6744316180397294094/?channel=video",
        "https://m.ixigua.com/i6738290326022128141/",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "toutiao"
        self.last_response = time.time()

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        js_file_path = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "special/generate_signature.js"
        )
        AS, CP, _signature = self.get_token(path=js_file_path)
        i = re.findall(".(\d{10,36})", webpage_url)[0]
        api = f'https://m.toutiao.com/i{i}/info/?_signature={_signature}&i={i}'
        response = await self.request(
            url=api,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua()),
            response_type="json"
        )
        result = self.extract_ipage(response=response)
        vid = result['vid']
        play_addr = await self.cal_play_addr(vid=vid, session=session)
        return self.merge_dicts(result, play_addr)

    @staticmethod
    def right_shift(val, n):
        return val >> n if val >= 0 else (val + 0x100000000) >> n

    async def cal_play_addr(self, vid, session):
        api = f'http://i.snssdk.com/video/urls/v/1/toutiao/mp4/{vid}'
        r = str(random.random())[2:]
        s = self.right_shift(binascii.crc32(f"{urlparse(api).path}?r={r}".encode()), 0)
        url = f"{api}?r={r}&s={s}"
        response = await self.request(
            url=url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua()),
        )
        video_json = json.loads(response)
        main_url = jmespath.search("max_by(data.video_list.*, &size).main_url", video_json)
        width = jmespath.search("max_by(data.video_list.*, &size).vwidth", video_json)
        height = jmespath.search("max_by(data.video_list.*, &size).vheight", video_json)
        try:
            duration = int(jmespath.search("data.video_duration", video_json))
        except:
            duration = None
        play_addr = base64.b64decode(main_url).decode()
        return {
            "play_addr": play_addr,
            "width": width,
            "height": height,
            "vid": jmespath.search("data.video_id", video_json),
            "duration": duration,
            "cover": jmespath.search("data.poster_url", video_json),
        }

    @staticmethod
    def extract_ipage(response):
        data = jmespath.search("data", response)
        result = {
            "author": jmespath.search("detail_source", data),
            "author_id": jmespath.search("media_user.id", data),
            "avatar": jmespath.search("media_user.avatar_url", data),
            "upload_ts": jmespath.search("publish_time", data),
            "view_count": jmespath.search("video_play_count", data),
            "title": jmespath.search("title", data),
            # "webpage_url": jmespath.search("url", data),
            "comment_count": jmespath.search("comment_count", data),
            "cover": jmespath.search("poster_url", data),
            "vid": jmespath.search("video_id", data),
            # "from": self.from_,
        }
        return result

    @staticmethod
    def get_token(path="../special/generate_signature.js"):
        """
        获取头条url中的各种token
        :return: as, cp, _signature
        """

        with open(path, "r") as js_file:
            lines = js_file.readlines()
            js_code = ""
            for line in lines:
                js_code += line
            context = execjs.compile(js_code)
            # the type of token is a str of json
            token = context.call('get_as_cp_signature')
            token_dict = json.loads(token)
            return token_dict['as'], token_dict['cp'], token_dict['_signature']


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

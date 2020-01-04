#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from urllib.parse import unquote
from scrapy import Selector
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://music\.163\.com/video/\w{20,40}/\?userid=\d{5,15}",
    ]

    TEST_CASE = [
        "分享台灣音樂風雲榜的视频《陈奕迅《苦瓜》唱尽世间百态，催人泪下！》http://music.163.com/video/9F01C451779850285AE78A477164A8C0/?userid=387580397 (@网易云音乐)",
        "分享非洲大使的视频《11.17 北京 木秦艾瑞欧《粉色苏打》》http://music.163.com/video/29AC8C00A0EE1B8EA609BEAF381727C9/?userid=387580397 (@网易云音乐)",
        "分享音乐小纸条儿的视频《咆哮吧，钢铁侠！AC/DC《Back In Black》这是摇滚老炮的怒吼！》http://music.163.com/video/30364DD42E8F33C7BD2A92DCA4E8DFED/?userid=387580397 (@网易云音乐)",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "网易云音乐"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua()),
        )
        results = self.extract(response=response)
        return results

    def extract(self, response):
        selector = Selector(text=response)
        mv = selector.css(".mv::attr('data-flashvars')").extract_first()
        mv_split = {unquote(ele).split("=", 1)[0]: unquote(ele).split("=", 1)[1] for ele in mv.split("&")}
        try:
            like_count, collect_count, forward_count = list(
                map(lambda x: x[1:-1], selector.css("#j-op a i::text").extract()))
        except:
            like_count = collect_count = forward_count = None
        result = {
            "play_addr": mv_split['hurl'] if mv_split.get("hurl", None) else mv_split['murl'],
            "title": mv_split.get("trackName", None),
            "author": mv_split.get("artistName", None),
            "vid": mv_split.get("resourceId", None),
            "cover": mv_split.get("coverImg", None),
            "width": mv_split.get("width", None),
            "height": mv_split.get("height", None),
            "upload_ts": self.string2timestamp(string="发布时间：2019-01-13", format="发布时间：%Y-%m-%d"),
            "like_count": like_count,
            "collect_count": collect_count,
            "forward_count": forward_count,
        }
        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

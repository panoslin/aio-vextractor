#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import re
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "http[s]://v.qq.com/",
    ]

    # downloader = 'ytd'

    TEST_CASE = [
        "腾讯视频 https://v.qq.com/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "tencent"
        self.output = []

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        # page = int(kwargs.pop("page", 1))
        headers = {
            'authority': 'v.qq.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://v.qq.com/channel/feeds_hotspot',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'pgv_pvi=3875408896; '
                      'pgv_si=s3355604992; '
                      'pgv_info=ssid=s5924370020; '
                      'pgv_pvid=7915709504; '
                      'ptisp=ctc; '
                      'RK=CipcjFKNEz; '
                      'ptcz=f6d402e9c10789384eb364aa9dda176d3c1dc11499f9ad63f6da78b7567e6e11; '
                      'tvfe_boss_uuid=23916d936281ff69; '
                      'ts_uid=8333726890; '
                      'bucket_id=9231008; '
                      'video_guid=30866b83caa1cbf2; '
                      'video_platform=2; '
                      'wsreq_logseq=317361767; '
                      'ts_refer=www.baidu.com/link; '
                      'ptag=www_baidu_com|multi_feed_V:\u901A\u680F\u529F\u80FD\u533A:\u901A\u680F\u6807\u9898; '
                      'ts_last=v.qq.com/; '
                      'ad_play_index=88; '
                      'qv_als=DBprLN6Sdn6qOGjAA11576726240aGSBSQ==',
        }
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        videoplus = \
        re.findall('<div class="mod_row_box" _wind="columnname=精选_原创精选([\s\S]*?)clearTimeout\(window.emptyPageTimer\)',
                   response)[0]
        sports_travel = re.findall(
            '<div class="mod_row_box" _wind="columnname=精选_体育资讯([\s\S]*?)<div class="mod_row_box" _wind="columnname=精选_时尚热度榜',
            response)[0]
        movie_target = re.findall(
            '<div class="mod_row_box" _wind="columnname=精选_电影预告([\s\S]*?)<div class="mod_row_box" _wind="columnname=精选_花絮·剧透·预告片',
            response)[0]
        auto = \
        re.findall('<div class="mod_row_box" _wind="columnname=精选_汽车资讯([\s\S]*?)<div .*?id="ad_qll_width3"', response)[
            0]

        videoplus_list = re.findall(
            '<a href="(.*?)"[\s\S]*?data-float="(.*?)"[\s\S]*?<img class="figure_pic" [ ]?\w+="(.*?)" alt="(.*?)"[\s\S]*?>',
            videoplus)
        sports_travel_list = re.findall(
            '<a href="(.*?)"[\s\S]*?data-float="(.*?)"[\s\S]*?<img class="figure_pic" [ ]?\w+="(.*?)" alt="(.*?)" [\s\S]*?>',
            sports_travel)
        movie_target_list = re.findall(
            '<a href="(.*?)"[\s\S]*?data-float="(.*?)"[\s\S]*?<img class="figure_pic" [ ]?\w+="(.*?)" alt="(.*?)" [\s\S]*?>',
            movie_target)
        auto_list = re.findall(
            '<a href="(.*?)"[\s\S]*?data-float="(.*?)"[\s\S]*?<img class="figure_pic" [ ]?\w+="(.*?)" alt="(.*?)" [\s\S]*?>',
            auto)

        url_vid_cover_title_s = videoplus_list + sports_travel_list + movie_target_list + auto_list
        for url_vid_cover_title in url_vid_cover_title_s:
            ele = dict()
            ele['webpage_url'] = url_vid_cover_title[0]
            ele['title'] = url_vid_cover_title[3]
            ele['cover'] = 'http:' + url_vid_cover_title[2]
            ele['vid'] = url_vid_cover_title[1]
            ele['playlist_url'] = webpage_url
            ele['from'] = self.from_
            self.output.append(ele)
        return self.output, False, {}

    # @staticmethod
    # def cal_duration(raw_duration_string):
    #     regex = re.compile("(\d{1,3}):?")
    #     _duration = regex.findall(raw_duration_string)
    #     duration = 0
    #     for num, i in enumerate(_duration[::-1]):
    #         duration += int(i) * (60 ** num)
    #     return duration


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2
        )
        pprint(res)

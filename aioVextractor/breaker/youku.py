#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import re
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www.youku.com/"
    ]

    TEST_CASE = [
        "https://www.youku.com/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "youku"
        self.output = []

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        headers = {
            'authority': 'www.youku.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '__ysuid=1575538493519Smd; '
                      'cna=DsZvFq/FGS0CAXF3GKayRVDM; '
                      '__ayft=1576029406821; '
                      'UM_distinctid=16ef2ac4848731-021c9cd4a0ed9f-31760856-1fa400-16ef2ac48491041; '
                      'juid=01drpaoi9a1k0f; '
                      'ycid=0; '
                      'seid=01druuqqifoot; '
                      'yseid=1576218225450BpkKN0; '
                      'yseidcount=2; '
                      'referhost=https%3A%2F%2Fapi.youku.com; '
                      '_m_h5_c=7ce9eb97f88dece74e202cc366513294_1576232617305%3B041fff907a603c6cc5e36cbf5fbb5c09; '
                      '__arycid=dz-3-00; '
                      '__arcms=dz-3-00; '
                      'seidtimeout=1576252524912; '
                      'ypvid=15762507251222E44Iy; '
                      'ysestep=130; '
                      'yseidtimeout=1576257925123; '
                      'ystep=143; '
                      '__ayvstp=972; '
                      'ctoken=jPDMl9DIxQLSwOfpipcF9HX-; '
                      '__aysid=1576719440710kvn; '
                      '__ayscnt=4; '
                      '__arpvid=1576738998609f3oqPa-1576738998645; '
                      '__aypstp=160; '
                      '__ayspstp=9; '
                      'CNZZDATA1277956573=1096885767-1576714228-https%253A%252F%252Fwww.baidu.com%252F%7C1576735828; '
                      'P_ck_ctl=C2DF09AE1B51F050534A8C9A4E3B4B8D; '
                      '_m_h5_tk=a567f4d9b471edd953409a22c5d7fee8_1576742779611; '
                      '_m_h5_tk_enc=79acc1d16eb95a67f21a23e307f6a074; '
                      'isg=BPPzrqzSqmERPmY-2T0wbTxfgv4dKIfqRE8oh6WRCZO_pBNGLfkxO8u-WpTvBN_i',
        }
        response = await self.request(
            url=webpage_url,
            headers=headers,
            session=session,
        )
        sports = re.findall('\[\{"title":"体育"[\s\S]*?\}\}\]', response)[0]
        music = re.findall('\[\{"title":"音乐"[\s\S]*?\}\}\]', response)[0]
        fashion_life = re.findall('\[\{"title":"生活"[\s\S]*?\}\}\]', response)[0]
        sports_music_life = sports + music + fashion_life
        cover_duration_vid_title_s = re.findall(
            '\{.*?"img":"(.*?)".*?"summary":"(.*?)".*?"videoId":"(.*?)".*?"title":"(.*?)".*?}',
            sports_music_life
        )
        for cover_duration_vid_title in cover_duration_vid_title_s:
            ele = dict()
            ele['webpage_url'] = f'https://v.youku.com/v_show/id_{cover_duration_vid_title[2]}.html'
            ele['title'] = cover_duration_vid_title[3]
            ele['cover'] = 'https://vthumb.ykimg.com/' + str(cover_duration_vid_title[0]).split('\\')[3]
            ele['vid'] = cover_duration_vid_title[2].replace("==", "")
            ele['duration'] = self.string2duration(
                cover_duration_vid_title[1],
                '%M:%S'
            )
            ele['playlist_url'] = webpage_url
            ele['from'] = self.from_
            self.output.append(ele)
        return self.output, False, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)

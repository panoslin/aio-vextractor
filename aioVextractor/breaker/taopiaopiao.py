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
        "http[s]://www.taopiaopiao.com/showList.htm",
        "http[s]?://h5.m.taopiaopiao.com/app/moviemain/pages/index/index.html"
    ]

    TEST_CASE = [
        "https://www.taopiaopiao.com/showList.htm",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "taopiaopiao"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        headers = {
            'authority': 'www.taopiaopiao.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://www.taopiaopiao.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 't=2aceb75f422d72041e046401bde95d7f; _tb_token_=bb33e003def5; cookie2=174d650e3d260d1820e048ef781ff4ea; cna=DsZvFq/FGS0CAXF3GKayRVDM; _m_h5_tk=726d913a054e2789119515c84ef8a739_1576668693527; _m_h5_tk_enc=b69776a1ff8881953ecc0dada8fb2ac0; dnk=%5Cu5C0F%5Cu6B66%5Cu7684%5Cu6B66%5Cu529F; uc1=cookie14=UoTbm8FIKp2WVg%3D%3D&pas=0&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&cookie21=URm48syIYB3rzvI4Dim4&cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&lng=zh_CN&existShop=false&tag=8; tracknick=%5Cu5C0F%5Cu6B66%5Cu7684%5Cu6B66%5Cu529F; lid=%E5%B0%8F%E6%AD%A6%E7%9A%84%E6%AD%A6%E5%8A%9F; csg=3e3cec9b; enc=aYx4wYc9e6fIvYTv15X%2FsmbvChTg%2F%2FA3RSlSwqX1fYw39D4UAukzinBtVY6Ge4DFWgIN8ulCtcCFL91YbVAVGw%3D%3D; isg=BD4-Rd_47xA2BTs0yVy9tBflj12AfwL5kbBVROhHqgF8i95lUA9SCWTpAxfiqPoR; l=dBLroImHqviG_NMSBOCanurza77OSIRYYuPzaNbMi_5d96TsaJQOkFGiSF96VjWVta8B4PCMyNy9-etUZkdfUNCPi9RLyv9JQhYC.',
        }

        params = (
            ('spm', 'a1z21.3046609.w2.3.1d69112aClJMGZ'),
            ('n_s', 'new'),
        )
        response = await self.request(
            url=webpage_url,
            headers=headers,
            session=session,
            params=params
        )
        output = []
        html = re.findall('<!-- 正在热映 -->[\s\S]*?<!-- 即将热映 -->',response)[0]
        vid_cover_title_s = re.findall('<a href=.*?showId=(\d+)&.*?class="movie-card">[\s\S]*?<img [\s\S]*? src="(.*?)">[\s\S]*?<span class="bt-l">(.*?)</span>',html)
        for vid_cover_title in vid_cover_title_s:
            ele = dict()
            ele['webpage_url'] = f'https://h5.m.taopiaopiao.com/app/dianying/pages/show-preview/index.html?from=outer&showid={vid_cover_title[0]}&sqm=dianying.h5.unknown.value&spm=a1z2r.7661912.home.d_440100_2_0_{vid_cover_title[0]}'
            ele['title'] = vid_cover_title[2]
            ele['cover'] = vid_cover_title[1]
            ele['vid'] = vid_cover_title[0]
            ele['playlist_url'] = webpage_url
            ele['from'] = self.from_
            output.append(ele)
        return output, False, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)

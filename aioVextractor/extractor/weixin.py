#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

import re, json
from bs4 import BeautifulSoup
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
from urllib.parse import unquote


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://mp\.weixin\.qq\.com/s/[\w-]{10,36}",
    ]

    TEST_CASE = [
        "https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw",
        "https://mp.weixin.qq.com/s/PZ0JBxMIAP5zVhsSxpxu7Q",
        # "http://mp.weixin.qq.com/s/2Y5rEq4HXtOAcHtYBNeebQ",
        "https://mp.weixin.qq.com/s/Ld6tw7ZjzFcUkPXa79HH5Q",
        "https://mp.weixin.qq.com/s/6lDIjP799J2b07RHoNil1A",
        "https://mp.weixin.qq.com/s/yjzmRFDEwJgXDfGaK_ooUQ",
        "https://mp.weixin.qq.com/s/WR6EdO8CYcpRHvsOM62Tdw",
        "https://mp.weixin.qq.com/s/kp3XI6eg53a3atJJMTeuSw",
        "https://mp.weixin.qq.com/s/DNxgcRlzGOuuu1ji5w5RRA",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weixin"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = {
            'authority': 'mp.weixin.qq.com',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )
        results = []
        iframes = re.findall('<iframe.*?data-cover="(.*?)".*?data-src="(.*?)">', text)
        if not iframes:
            iframes = re.findall('<iframe.*?class="(.*?)".*?data-src="(.*?)">', text)
        for iframe in iframes:
            item = dict()
            selector = BeautifulSoup(text, 'lxml')
            title = selector.find('h2', attrs={"class": "rich_media_title"})
            item['title'] = title.text.strip()
            author = selector.find('a', attrs={"id": "js_name"})
            item['author'] = author.text.strip()
            # item['cover_list'] = selector.find('img', attrs={"class": "rich_pages "})
            item['play_addr'] = iframe[-1].replace(";", "&")
            item['vid'] = iframe[-1].split(';')[-1].strip("vid=")
            if re.match("https://mp.weixin.qq.com/mp/readtemplate", item['play_addr']):
                item['play_addr'] = await self.parse(item['vid'], session)
            else:
                item = self.merge_dicts(
                    item,
                    (await self.extract_iframe(iframe_url=item['play_addr'], session=session))[0]
                )

            item['cover'] = unquote(iframe[0])
            if re.match('video_iframe',item['cover']):
                item['cover'] = f'http://vpic.video.qq.com/97153782/{item["vid"]}.png'
            results.append(item)
        return results

    async def parse(self, vid, session):
        json_url = f'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_play_url&preview=0&__biz=MzU0ODE3Nzc4Nw==&mid=2247525077&idx=1&vid={vid}&uin=&key=&pass_ticket=&wxtoken=777&appmsg_token=&x5=0&f=json'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        texts = await self.request(
            url=json_url,
            session=session,
            headers=headers
        )
        html = json.loads(texts)
        return html['url_info'][0]['url']


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from bs4 import BeautifulSoup
import re, json, time
import traceback
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://lanfanapp\.com/recipe/\d{1,6}",
    ]

    TEST_CASE = [
        "https://lanfanapp.com/recipe/3127/",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "lanfanapp"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        text = await self.request(
            url=webpage_url,
            session=session,

        )
        item = dict()
        soup = BeautifulSoup(text, 'lxml')
        video = soup.find("video", attrs={"id": "recipe-media"})
        # item['from'] = self.from_
        # item['webpage_url'] = webpage_url
        item['cover'] = video.get("poster")
        item['play_addr'] = video.get("src")
        item['width'] = video.get("width")
        item['height'] = video.get("height")
        h1 = soup.find("h1", attrs={"class": "recipe-name title-1"})
        if h1:
            item['title'] = h1.text
        font = soup.find("div", attrs={'class': "recipe-meta-item score"})
        if font:
            try:
                score = font.text.strip().replace("评分", "").strip()
                item['rating'] = score
            except:
                pass
        jsonstr = re.findall("window.__NUXT__=(.*?);<", text)
        if jsonstr:
            try:
                jsondata = json.loads(jsonstr[0])['data'][0]['recipe']
                item['collect_count'] = jsondata['n_collects']
                item['comment_count'] = jsondata['n_comments']
                item['vid'] = jsondata.get('id')
                item['description'] = jsondata.get('desc')
                try:
                    item['upload_ts'] = jsondata.get("create_time")
                    item['upload_ts'] = int(time.mktime(time.strptime(item['upload_ts'], "%Y-%m-%d %H:%M:%S")))
                except:
                    traceback.print_exc()
            except:
                traceback.print_exc()
        return item

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/28/19
# IDE: PyCharm

import jmespath
import re
import time
from scrapy.selector import Selector
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://blog\.naver\.com/PostView\.nhn\?blogId=\w*?&logNo=\d{9,15}",
        "http[s]?://blog\.naver\.com/PostList\.nhn\?blogId=\w*",
    ]

    TEST_CASE = [
        "http://blog.naver.com/PostList.nhn?blogId=paranzui&categoryNo=0&from=postList",
        "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221233413302&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11",
        "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221239676910&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11",
        "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221227458497&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=29&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=29",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "naver"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        response_text = await self.request(
            url=webpage_url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua())
        )
        # async with session.get(webpage_url, headers=self.general_headers(user_agent=self.random_ua())) as response:
        #     response_text = await response.text(encoding='utf8', errors='ignore')
        selector = Selector(text=response_text)
        # iframe_url = selector.css('iframe[src*=vid]::attr(src)').extract_first()
        vid = re.findall('vid="(\w{36})"', response_text)[0]
        inKey = re.findall('key="(\w{20,100})"', response_text)[0]
        # inKey = parse_qs(urlparse(iframe_url).query)['inKey'][0]
        result = dict()
        result['avatar'] = selector.css('.bloger .thumb img::attr(src)').extract_first().split('?')[0]
        author_videoNum = selector.css('.category_title::text').re('([\d|,]*)')
        result['author_videoNum'] = sorted(author_videoNum)[-1].replace(',', '')
        result['vid'] = vid
        # result['from'] = self.from_
        result['upload_ts'] = self.format_upload_ts(selector.css("p[class*='_postAddDate']::text").extract_first())
        # result['webpage_url'] = webpage_url
        VideoJson = await self.request_naver_api(iframe_url=webpage_url, in_key=inKey, session=session, vid=vid)
        return self.extract(video_json=VideoJson, result=result)

    @RequestRetry
    async def request_naver_api(self, iframe_url, in_key, session, vid):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = iframe_url
        headers['Origin'] = "http://serviceapi.nmv.naver.com"
        params = {'key': in_key,
                  'pid': f'rmcPlayer_{int(time.time() * 10 ** 7)}',
                  'sid': '2',
                  'ver': '2.0',
                  'devt': 'html5_mo',
                  'doct': 'json',
                  'ptc': 'http',
                  'sptc': 'http',
                  'cpt': 'vtt',
                  'ctls': '{"visible":{"fullscreen":true,"logo":false,"playbackRate":false,"scrap":true,"playCount":true,"commentCount":true,"title":true,"writer":false,"expand":false,"subtitles":true,"thumbnails":true,"quality":true,"setting":true,"script":false,"logoDimmed":true,"badge":true,"seekingTime":true,"linkCount":true,"createTime":false,"thumbnail":true},"clicked":{"expand":false,"subtitles":false}}',
                  'pv': '4.8.45',
                  'dr': '1920x1080',
                  'lc': 'ko_KR'}
        naver_api = 'http://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{vid}'.format(vid=vid)
        video_json = await self.request(
            url=naver_api,
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        # async with session.get(naver_api, headers=headers, params=params) as response:
        #     VideoJson = await response.json()
        return video_json

    @staticmethod
    def format_upload_ts(upload_ts):
        """
        input: '2018. 3. 20. 22:14'

        """
        try:
            return int(time.mktime(time.strptime(upload_ts, '%Y. %m. %d. %H:%M'))) if upload_ts else None
        except:
            return None

    @staticmethod
    def extract(video_json, result):
        result['author'] = jmespath.search('meta.user.name', video_json)
        result['play_addr'] = jmespath.search("max_by(videos.list, &size).source", video_json)
        result['title'] = jmespath.search('meta.subject', video_json)
        result['cover'] = jmespath.search('meta.cover.source', video_json)
        video_duration = jmespath.search('videos.list[0].duration', video_json)
        result['duration'] = int(video_duration) if video_duration else None
        return result

    @staticmethod
    def extract_play_addr(video_json):
        play_addr_list = dict()
        for size, src in jmespath.search('videos.list[].[size, source]', video_json):
            play_addr_list[size] = src
        if len(play_addr_list) == 1:
            play_addr = play_addr_list[max(play_addr_list)]
        else:
            if None in play_addr_list:
                del play_addr_list[None]
            play_addr = play_addr_list[max(play_addr_list)]
        return play_addr


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

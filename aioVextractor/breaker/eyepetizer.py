#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import traceback
import re
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from aioVextractor.utils import RequestRetry


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www\.eyepetizer\.net/pgc\.html\?.*",
        "http[s]?://www\.eyepetizer\.net/tag\.html\?.*",
        "http[s]?://baobab\.kaiyanapp\.com/api/v1/tag/videos\?id=.*"
    ]

    TEST_CASE = [
        "https://www.eyepetizer.net/pgc.html?deviceModel=iPhone&pid=22&utm_source=wechat-moments&vc=6312&vn=5.9.0&udid=324851f6406581f1ec04d1eff1d8198e508abf64&utm_campaign=routine&uid=0&utm_medium=share",
        "https://www.eyepetizer.net/tag.html?vc=6312&utm_medium=share&utm_source=wechat-moments&vn=5.9.0&deviceModel=iPhone&tid=1019&udid=3b94062b8c5d6a875a30557d6543e0128765a641&utm_campaign=routine",

        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=16&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=12&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1022&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=2&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1019&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1025&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=24&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1018&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1024&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1020&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=30&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=1023&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=140&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=26&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=666&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=28&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
        'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=32&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813',
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "eyepetizer"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        if re.match("http[s]?://www\.eyepetizer\.net/tag\.html\?.*", webpage_url):
            tid = re.findall("tid=(\d{1,8})", webpage_url)[0]
            response = await self.retrieve_tag_paging_api(tid=tid, page=page, session=session)
            results = self.extract_tag_pageing_api(response_json=response, playlist_url=webpage_url)
            return results
        elif re.match("http[s]?://www\.eyepetizer\.net/pgc\.html\?.*", webpage_url):
            if page > 1:
                apiUrl = kwargs['nextPageUrl']
            else:
                pid = re.findall("pid=(\d{1,10})", webpage_url)[0]
                apiUrl = await self.retrieve_pgc(pgc_id=pid, session=session)
            response = await self.request_user_info(session=session, webpage_url=apiUrl)
            results = self.extract_user_info(response_json=response, playlist_url=webpage_url)
            return results
        else:
            headers = {
                'authority': 'baobab.kaiyanapp.com',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'cookie': 'sajssdk_2015_cross_new_user=1; '
                          'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216f11663aaf5bb-009f6059607723-31760856-2073600-16f11663ab0a31%22%2C%22%24device_id%22%3A%2216f11663aaf5bb-009f6059607723-31760856-2073600-16f11663ab0a31%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_utm_source%22%3A%22eyepetizer-homepage%22%2C%22%24latest_utm_medium%22%3A%22internal%22%2C%22%24latest_utm_campaign%22%3A%22routine%22%7D%7D',
            }
            if page > 1:
                nextPageUrl = kwargs['nextPageUrl']
                response = await self.request(
                    url=nextPageUrl,
                    headers=headers,
                    # params=params,
                    session=session,
                    response_type="json",
                )
            else:
                vid = re.findall("id=(\d{1,4})", webpage_url)[0]
                params = (
                    ('id', vid),
                    ('f', 'iphone'),
                    ('net', 'wifi'),
                    ('p_product', 'EYEPETIZER_IOS'),
                    ('size', '414.0X736.0'),
                    ('v', '5.4.1'),
                    ('vc', '5813'),
                )
                # api = 'https://baobab.kaiyanapp.com/api/v1/tag/videos?id=16&f=iphone&net=wifi&p_product=EYEPETIZER_IOS&size=414.0X736.0&v=5.4.1&vc=5813'
                # api = 'https://www.kaiyanapp.com/detail.html?vid=179056&utm_source=eyepetizer-homepage&utm_medium=internal&utm_campaign=routine'
                response = await self.request(
                    url=webpage_url,
                    headers=headers,
                    params=params,
                    session=session,
                    response_type="json",
                )
            results = self.extract(response=response, webpage_url=webpage_url)
            return results

    @RequestRetry
    async def retrieve_tag_paging_api(self, tid, session, page):
        cookies = {
            'ky_auth': '',
            'sdk': '25',
        }

        headers = {
            'model': 'Android',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; vivo X9 Build/N2G47H)',
            'Host': 'baobab.kaiyanapp.com',
        }
        if page == 1:
            params = (
                ('id', str(tid)),
                ('udid', '07666c901e294e9d9a85bdb97c50ee333c666719'),
                ('vc', '551'),
                ('vn', '5.9.1'),
                ('size', '1080X1920'),
                ('deviceModel', 'vivo X9'),
                ('first_channel', 'eyepetizer_vivo_market'),
                ('last_channel', 'eyepetizer_vivo_market'),
                ('system_version_code', '25'),
            )
        else:
            start = page * 10
            params = (
                ('start', str(start)),
                ('num', '10'),
                ('strategy', 'date'),
                ('id', str(tid)),
                ('udid', '07666c901e294e9d9a85bdb97c50ee333c666719'),
                ('vc', '551'),
                ('vn', '5.9.1'),
                ('size', '1080X1920'),
                ('deviceModel', 'vivo X9'),
                ('first_channel', 'eyepetizer_vivo_market'),
                ('last_channel', 'eyepetizer_vivo_market'),
                ('system_version_code', '25'),
            )
        api = 'http://baobab.kaiyanapp.com/api/v1/tag/videos'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            cookies=cookies,
            response_type="json"
        )
        return response

    def extract_tag_pageing_api(self, response_json, playlist_url):
        results = []
        itemList = jmespath.search("itemList[].data", response_json)
        has_more = True if jmespath.search("nextPageUrl", response_json) else False
        for ele in itemList:
            data = jmespath.search("content.data", ele)
            if data is None:
                data = ele
            try:
                data['title']
            except:
                continue
            tag = jmespath.search("tags[].name", data)
            try:
                upload_ts = data['releaseTime'] // 1000
            except:
                upload_ts = None
            try:
                result = {
                    "cover": jmespath.search("cover.feed", data),
                    "play_addr": jmespath.search("playUrl", data),
                    "tag": tag,
                    "category": data['category'],
                    "description": data['description'],
                    "title": data['title'],
                    "author": data['author']['name'],
                    "author_id": data['author']['id'],
                    "upload_ts": upload_ts,
                    "vid": data['id'],
                    "duration": data['duration'],
                    "from": self.from_,
                    "playlist_url": playlist_url,
                    "webpage_url": jmespath.search("webUrl.forWeibo", data),
                }
            except:
                traceback.print_exc()
                continue
            results.append(result)
        else:
            return results, has_more, {}

    @RequestRetry
    async def retrieve_pgc(self, pgc_id, session):
        headers = {
            'Host': 'baobab.kaiyanapp.com',
            'user-agent': 'Eyepetizer/6312 CFNetwork/978.0.7 Darwin/18.7.0',
            'accept': '*/*',
            'accept-language': 'zh-cn',
        }

        params = (
            # ('_s', 'f8913ad17d6b86e2efe5cc69a8820928'),
            ('f', 'iphone'),
            ('id', str(pgc_id)),
            ('net', 'wifi'),
            ('p_product', 'EYEPETIZER_IOS'),
            ('size', '414.0X896.0'),
            # ('u', '324851f6406581f1ec04d1eff1d8198e508abf64'),
            ('userType', 'PGC'),
            ('v', '5.9.0'),
            ('vc', '6312'),
        )
        api = 'https://baobab.kaiyanapp.com/api/v5/userInfo/tab'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        return jmespath.search("tabInfo.tabList[1].apiUrl", response)

    @RequestRetry
    async def request_user_info(self, session, webpage_url):
        headers = {
            'Host': 'baobab.kaiyanapp.com',
            'user-agent': 'Eyepetizer/6312 CFNetwork/978.0.7 Darwin/18.7.0',
            'accept': '*/*',
            'accept-language': 'zh-cn',
        }
        response = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            response_type="json"
        )
        return response

    def extract_user_info(self, response_json, playlist_url):
        has_next = jmespath.search("nextPageUrl", response_json)
        nextPageUrl = jmespath.search("nextPageUrl", response_json)
        itemList = jmespath.search("itemList[].data.content.data", response_json)
        results = []
        for ele in itemList:
            try:
                results.append(
                    {
                        "vid": ele['id'],
                        "title": ele['title'],
                        "description": ele['description'],
                        "tag": jmespath.search("tags[].name", ele),
                        "collect_count": jmespath.search("consumption.collentionCount", ele),
                        "share_count": jmespath.search("consumption.shareCount", ele),
                        "category": ele['category'],
                        "author": jmespath.search("author.name", ele),
                        "author_id": jmespath.search("author.id", ele),
                        "author_videoNum": jmespath.search("author.videoNum", ele),
                        "avatar": jmespath.search("author.icon", ele),
                        "cover": jmespath.search("cover.feed", ele),
                        "play_addr": jmespath.search("playUrl", ele),
                        "duration": jmespath.search("duration", ele),
                        "webpage_url": jmespath.search("webUrl.forWeibo", ele),
                        "upload_ts": jmespath.search("releaseTime", ele),
                        "from": self.from_,
                        "playlist_url": playlist_url,
                    }
                )
            except:
                continue
        return results, has_next, {"nextPageUrl": nextPageUrl}

    def extract(self, response, webpage_url):
        has_next = jmespath.search("nextPageUrl", response)
        nextPageUrl = jmespath.search("nextPageUrl", response)
        datas = jmespath.search('itemList[*].data.content.data', response)
        item_list = []
        for item in datas:
            try:
                if item['updateTime'] is not int:
                    upload_ts = 0
                else:
                    upload_ts = item['updateTime']
                item_list.append({
                    "vid": item['id'],
                    "cover": jmespath.search("cover.*", item)[0],
                    "description": item['description'],
                    "title": item['title'],
                    "author": jmespath.search("author.name", item),
                    "from": self.from_,
                    "playlist_url": webpage_url,
                    "webpage_url": jmespath.search("webUrl.*", item)[0],
                    "forward_count": jmespath.search("consumption.replyCount", item),
                    "collect_count": jmespath.search("consumption.collectionCount", item),
                    "share_count": jmespath.search("consumption.shareCount", item),
                    "view_count": jmespath.search("consumption.playCount", item),
                    "upload_ts": upload_ts,
                })
            except:
                traceback.print_exc()
                continue
        return item_list, has_next, {"nextPageUrl": nextPageUrl}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            page=2,
            nextPageUrl='https://baobab.kaiyanapp.com/api/v1/tag/videos?start=10&num=10&strategy=date&id=16'
        )
        pprint(res)

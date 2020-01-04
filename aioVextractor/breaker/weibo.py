#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
import re
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://weibo\.com/p/\d{5,36}",
        "http[s]?://weibo\.com/[\w\.-]{5,36}",
        "http[s]?://weibo\.com/u/\d{5,30}",
    ]

    # downloader = 'ytd'

    TEST_CASE = [
        'https://weibo.com/p/1005055882998192/photos?type=video#place',  ## miao pai
        "https://weibo.com/kongxiaorui?refer_flag=1005055014_",
        "https://weibo.com/u/1927564525",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "weibo"

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        try:
            uid = re.findall("https://weibo\.com/u/(\d{4,20})", webpage_url)[0]
        except IndexError:
            user_page_response = await self.request_user_home_page(webpage_url=webpage_url, session=session)
            try:
                uid = re.findall("CONFIG\['oid'\]='(\d{4,20})';", user_page_response)[0]
            except:
                return False

        page = int(kwargs.pop("page", 1))
        if page > 1:
            container_id = kwargs['container_id']
            since_id = kwargs['since_id']
            response_user_video_page = await self.request_user_video_page(
                container_id=container_id,
                session=session,
                since_id=since_id
            )
            results = self.extract_user_video_page(
                response=response_user_video_page,
                container_id=container_id,
                webpage_url=webpage_url,
            )
            return results
        else:
            response_fid = await self.request_fid(
                uid=uid,
                session=session
            )
            profile = self.extract_profile(
                response=response_fid,
                webpage_url=webpage_url
            )
            container_id = profile['container_id']
            response_user_video_page = await self.request_user_video_page(
                container_id=container_id,
                session=session
            )
            results = self.extract_user_video_page(
                response=response_user_video_page,
                container_id=container_id,
                webpage_url=webpage_url,
            )
            return results

    @RequestRetry
    async def request_fid(self, uid, session):
        headers = {
            'Host': 'api.weibo.cn',
            'user-agent': 'Weibo/38575 (iPhone; iOS 12.4.1; Scale/2.00)',
            'snrt': 'normal',
            'accept': '*/*',
        }

        params = (
            ('skin', 'default'),
            ('c', 'iphone'),
            ('lang', 'zh_CN'),
            ('s', '9ad46666'),
            ('ua', 'iPhone11,8__weibo__9.10.1__iphone__os12.4.1'),
            ('sensors_is_first_day', 'true'),
            ('from', '109A193010'),
            ('user_domain', str(uid)),
        )

        api = 'https://api.weibo.cn/2/profile'
        async with session.get(api, headers=headers, params=params) as response:
            response_json = await response.json()
            return response_json

    @staticmethod
    def extract_profile(response, webpage_url):
        userInfo = jmespath.search("userInfo", response)
        tabsInfo = jmespath.search("tabsInfo", response)
        profile = {
            "author": jmespath.search("screen_name", userInfo),
            "author_id": jmespath.search("id", userInfo),
            "author_description": jmespath.search("description", userInfo),
            "avatar": jmespath.search("avatar_hd", userInfo),
            "author_url": webpage_url,
            "container_id": list(filter(lambda x: x["tab_type"] == "video",
                                        jmespath.search('tabs[:].{"container_id":containerid, "tab_type":tab_type}',
                                                        tabsInfo)))[0]["container_id"],
        }
        return profile

    async def request_user_video_page(self, container_id, session, since_id=None):
        headers = {
            'Host': 'api.weibo.cn',
            'user-agent': 'Weibo/38575 (iPhone; iOS 12.4.1; Scale/2.00)',
            'snrt': 'normal',
            'accept': '*/*',
        }
        api = 'https://api.weibo.cn/2/cardlist'
        if since_id:
            params = (
                ('skin', 'default'),
                ('c', 'iphone'),
                ('lang', 'zh_CN'),
                ('s', '9ad46666'),
                ('sensors_is_first_day', 'false'),
                ('sensors_mark', '0'),
                ('ft', '1'),
                ('gsid',
                 '_2AkMq9XIEf8NhqwJRmfwVymnra4l3wgjEieKcqYPfJRM3HRl-wT9kqncMtRV6AXo2kC2fXrU2efujvgL2TpAgzzkjnNOM'),
                ('from', '109A193010'),
                ('fid', str(container_id)),
                ('count', '20'),
                ('containerid', str(container_id)),
                ('since_id', str(since_id)),
            )

        else:
            params = (
                ('skin', 'default'),
                ('c', 'iphone'),
                ('lang', 'zh_CN'),
                ('s', '9ad46666'),
                ('v_f', '1'),
                ('sensors_mark', '0'),
                ('ft', '0'),
                ('uid', '1014062974080'),
                ('v_p', '76'),
                ('gsid',
                 '_2AkMq9aZwf8NhqwJRmfwVymnra4l3wgjEieKcqVerJRM3HRl-wT9jqlA9tRV6AXo2kH6s9Kwin4lgSI19gT9C8rdUnvk-'),
                ('from', '109A193010'),
                ('fid', str(container_id)),
                ('count', '20'),
                ('containerid', str(container_id)),
                ('page', '1'),
            )

        return await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )

    def extract_user_video_page(self, response, container_id, webpage_url):
        results = []
        cards = jmespath.search("cards[].mblog", response)
        has_next = jmespath.search("cardlistInfo.since_id", response)
        since_id = jmespath.search("cardlistInfo.since_id", response)
        for ele in cards:
            try:
                results.append({
                    "title": None,
                    "vid": ele['idstr'],
                    "description": ele['text'],
                    "author": jmespath.search("user.name", ele),
                    "author_id": jmespath.search("user.idstr", ele),
                    "webpage_url": jmespath.search("url_struct[0].short_url", ele),
                    "from": self.from_,
                    "playlist_url": webpage_url,
                    "cover": jmespath.search("page_info.pic_info.pic_big.url", ele),
                })
            except:
                continue
        else:
            return results, True if has_next else False, {"since_id": since_id, "container_id": container_id}

    @RequestRetry
    async def request_user_home_page(self, webpage_url, session):
        cookies = {
            'YF-Page-G0': '761bd8cde5c9cef594414e10263abf81|1571640560|1571640560',
            'SUB': '_2AkMq8dvDf8NxqwJRmP8QzGjiZYVyzQHEieKcrSoYJRMxHRl-yT83qkM8tRB6AXH1LJWf74XoNwusfXyh_hIC1ivE9Rbj',
            'SUBP': '0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5UspoP1zWKfoH4SC2cgSGC',
        }

        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }

        return await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            cookies=cookies
        )


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[2],
            # param={'container_id': '2315671927564525', 'since_id': '4410894844801007kp2'}
        )
        pprint(res)

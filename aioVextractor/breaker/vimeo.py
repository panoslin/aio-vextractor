#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from urllib.parse import urlsplit
import jmespath
import re
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "https://vimeo\.com/[\w]*",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://vimeo.com/alitasmitmedia",
        "https://vimeo.com/watch",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "vimeo"
        self.results = []

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        if re.match('https://vimeo.com/watch', webpage_url):
            cookies = {
                'vuid': 'pl670264717.896616083',
                'player': '',
                '_gcl_au': '1.1.1819768473.1576216511',
                '_ga': 'GA1.2.1234020019.1576216511',
                '_fbp': 'fb.1.1576216513685.1362106431',
                '_mibhv': 'anon-1576740506084-1619758065_6631',
                '_micpn': 'esp:-1::1576740506084',
                '__qca': 'P0-392378184-1576740506277',
                '__ssid': '1b5cbaff-cbc6-4685-9fbf-f2cbe2c20010',
                '_gcl_dc': 'GCL.1576740591.EAIaIQobChMIjYbApJjB5gIViXZgCh0yWQLHEAAYASAAEgI7KvD_BwE',
                '_gcl_aw': 'GCL.1576740599.EAIaIQobChMIjYbApJjB5gIViXZgCh0yWQLHEAAYASABEgKuGvD_BwE',
                '_gac_UA-76641-8': '1.1576740599.EAIaIQobChMIjYbApJjB5gIViXZgCh0yWQLHEAAYASABEgKuGvD_BwE',
                'SnapABugHistory': '1#',
                'SnapABugVisit': '1#1576740604',
                'continuous_play_v3': '1',
                '_abexps': '%7B%22982%22%3A%22control%22%2C%221024%22%3A%22plans%3Dbusiness%2ClivePremium%2Centerprise%22%2C%221038%22%3A%22variant%22%7D',
                '_gid': 'GA1.2.77077102.1577063741',
            }

            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'Sec-Fetch-User': '?1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Referer': 'https://vimeo.com/',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            response = await self.request(
                url=webpage_url,
                session=session,
                cookies=cookies,
                headers=headers,
            )
            html = re.findall('vimeo.explore_data = \{(.*?)};', response)[0]
            html = str(html).replace('\\', '')
            items = re.findall('(\{"uniqid":"\d+","type":"standard_multi",.*?"collection_items":.*)', html)[0]
            premieres_ = re.findall('\{.*?"text":"Staff Pick Premieres",', items)[0]
            awards_ = re.findall('"follow_title":"Branded Content",(.*?)"text":"Action-packed sports",', items)[0]
            commercials_ = re.findall('"follow_title":"Title Sequences",(.*?)"text":"Commercials",', items)[0]
            videos_ = re.findall('"text":"Comedy on Vimeo",(.*?)"text":"Explore the best 360 videos on Vimeo",', items)[
                0]

            html = premieres_ + awards_ + commercials_ + videos_
            # [视频id,视频图片,视频名字,用户id,用户昵称,用户url,用户头像]
            collection_items = re.findall(
                '\{"clip_id":(\d+),.*?"thumbnail".*?"src_8x":"(.*?)",.*?,"title":"(.*?)",.*?"user".*?"id":(\d+),"name":"(.*?)","url":"(.*?)",.*?"thumbnail".*?"src_8x":"(.*?)".*?}',
                html)
            for collection_item in collection_items:
                ele = dict()
                ele['vid'] = collection_item[0]
                ele['cover'] = collection_item[1]
                ele['title'] = collection_item[2]
                ele['author_id'] = collection_item[3]
                ele['author'] = collection_item[4]
                ele['author_url'] = 'https://vimeo.com' + collection_item[5]
                ele['author_avatar'] = collection_item[6]
                ele['playlist_url'] = webpage_url
                ele['from'] = self.from_
                ele['webpage_url'] = 'https://vimeo.com/' + collection_item[0]

                self.results.append(ele)
            return self.results, False, {}

        else:
            ParseResult = urlsplit(webpage_url)
            path = ParseResult.path
            if re.match('/channels/.*', path):  ## https://vimeo.com/channels/ceiga
                ## do not supported
                return []
            elif re.match('/\d{6,11}', path):  ## https://vimeo.com/281493330  ## this is single
                return []
            elif re.match('[/.*]', path):  ## https://vimeo.com/alitasmitmedia
                headers = {
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'User-Agent': self.random_ua(),
                    'Accept': '*/*',
                    'X-Requested-With': 'XMLHttpRequest',
                }

                clips = await self.request(
                    url=webpage_url,
                    session=session,
                    headers=headers,
                    params={'action': 'get_profile_clips',
                            'page': page},
                    response_type="json"
                )
                results = jmespath.search('clips[].{'
                                          '"title": title, '
                                          '"cover": thumbnail.src, '
                                          # '"cover": thumbnail.src_8x, '
                                          '"duration": duration.raw, '
                                          '"vid": clip_id, '
                                          '"webpage_url": url, '
                                          '"recommend": is_staffpick, '
                                          '"comment_count": quickstats.total_comments.raw, '
                                          '"like_count": quickstats.total_likes.raw, '
                                          '"view_count": quickstats.total_plays.raw, '
                                          '"author": user.name, '
                                          '"author_id": user.id, '
                                          '"author_url": user.url, '
                                          '"author_avatar": user.thumbnail.src_8x}', clips)
                for ele in results:
                    ele['author_url'] = "https://vimeo.com" + ele['author_url']
                    ele['webpage_url'] = "https://vimeo.com" + ele['webpage_url']
                    ele['playlist_url'] = webpage_url
                    ele['from'] = self.from_

                has_next = jmespath.search('clips_meta.has_next', clips)
                return results, has_next, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)

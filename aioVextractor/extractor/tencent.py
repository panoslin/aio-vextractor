#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from random import choice
from urllib.parse import urlparse, parse_qs
import traceback
import jmespath
import math
import random
import re
import os
from scrapy.selector import Selector
import time
import asyncio
from aioVextractor.extractor.tool_set import (
    ToolSet,
    validate,
    RequestRetry
)
import platform
if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

class Extractor(ToolSet):
    target_website = [
        "http[s]?://v\.qq\.com/x/page/\w{5,20}\.html",
        "http[s]?://v\.qq\.com/x/cover/\w{5,20}\.html",
        "http[s]?://v\.qq\.com/x/cover/[\w/]{5,36}\.html",
        "http[s]?://v\.qq\.com/iframe/player\.html\?vid=\w{5,20}",
        "http[s]?://v\.qq\.com/iframe/preview.html\?.*?vid=\w{5,20}",
        "http[s]?://v\.qq\.com/txp/iframe/player.html\?.*?vid=\w{5,20}",
        "http[s]?://m\.v\.qq\.com/x/cover/.*",
        "http[s]?://m\.v\.qq\.com/x/page/.*",
        "http[s]?://m\.v\.qq\.com/play/.*",
        "http[s]?://m\.v\.qq\.com/play\.html\?.*",
    ]

    TEST_CASE = [
        "https://v.qq.com/x/page/s0886ag14xn.html",
        "https://v.qq.com/x/page/n0864edqzkl.html",
        "https://v.qq.com/x/page/s08899ss07p.html",
        "https://v.qq.com/x/cover/bzfkv5se8qaqel2.html",
        "https://v.qq.com/iframe/player.html?vid=c0912n1rqrw&tiny=0&auto=0",
        "https://v.qq.com/iframe/preview.html?width=500&height=375&auto=0&vid=m0927lumf50",
        "https://v.qq.com/iframe/preview.html?width=500&height=375&auto=0&vid=m0927lumf50",
        "https://v.qq.com/x/cover/lkc4yiuejqzwgtx/b0021dk5cc6.html",
        "https://v.qq.com/txp/iframe/player.html?vid=a3009mlsv3t",
        "http://m.v.qq.com/x/cover/x/mzc0020085uj8bx/p0032pk4i8i.html?&ptag=4_7.6.0.22280_copy",
        "https://m.v.qq.com/x/page/c/b/0/c30080f80b0.html?ptag=4_7.6.5.22283_copy",
        "http://m.v.qq.com/play/play.html?vid=c30080f80b0&ptag=4_7.6.5.22283_copy",
        "https://m.v.qq.com/play.html?cid=&vid=w3023g0wmfg",
        "https://m.v.qq.com/play.html?cid=&vid=n0032104nww",
    ]

    def __init__(self, *args, **kwargs):
        ToolSet.__init__(self, *args, **kwargs)
        self.from_ = "tencent"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        try:
            vid = parse_qs(urlparse(webpage_url).query).get('vid')[0]
            webpage_url = 'https://v.qq.com/x/page/{vid}.html'.format(vid=vid)
        except (IndexError, TypeError):
            webpage_url = webpage_url
            vid = None
        headers = {'authority': 'v.qq.com',
                   'upgrade-insecure-requests': '1',
                   'user-agent': self.random_ua(),
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        if not vid:
            try:
                vid = re.findall('&vid=(\w{5,15})&?', text)[0]
            except (TypeError, IndexError):
                vid = re.findall('(\w{11})\.html', text)[0]
        selector = Selector(text=text)
        result, commentId = self.extract(response=text, vid=vid)
        gather_results = await asyncio.gather(*[
            self.extract_comment_count(commentId=commentId, session=session),
            self.extract_author_info(selector=selector, session=session),
            self.extract_by_vkey(vid=vid, url=webpage_url, session=session)
        ])
        result = self.merge_dicts(result, *gather_results)
        return result

    def extract(self, response, vid):
        selector = Selector(text=response)
        try:
            title = selector.css('meta[name*=title]::attr(content)').extract_first()
            title = title.replace('_1080P在线观看平台_腾讯视频', ''). \
                replace('高清1080P在线观看平台', ''). \
                replace('_腾讯视频', ''). \
                replace('_', ' ')
        except AttributeError:
            title = selector.css('.player_title a::text').extract_first()
        if not title:
            title = selector.css(".video_tit::text").extract_first()
        category = selector.css('.site_channel .channel_nav[class~="current"]::text').extract()
        tag = selector.css("head meta[name*='keywords']::attr(content)").extract_first()
        video_create_time = selector.css('head meta[itemprop="datePublished"]::attr(content)').extract_first()
        upload_ts, upload_date = self.strptime(video_create_time)
        upload_ts = upload_ts
        if upload_ts is None:
            upload_ts = self.strptime(selector.css(".video_info .date::text").extract_first())[0]
        duration = selector.css('head meta[itemprop="duration"]::attr(content)').extract_first()
        duration = self.cal_duration(duration)
        if duration is None:
            VIDEO_INFO = selector.css('script[r-notemplate]').re_first('var VIDEO_INFO = ([\s|\S]*)\s</script>')
            try:
                VIDEO_INFO = json.loads(VIDEO_INFO)  ## having tag inside
            except (ValueError, TypeError):
                duration = None
            else:
                duration = jmespath.search("duration", VIDEO_INFO)
        view_count_type = selector.css('.action_count .icon_text::text').extract_first()
        view_count_type = view_count_type if view_count_type  else ''
        if '专辑' in view_count_type:
            COVER_INFO = selector.css('script[r-notemplate]').re_first('var COVER_INFO = ([\s|\S]*?)\svar')
            try:
                COVER_INFO = json.loads(COVER_INFO)  ## having category_map inside
            except ValueError:
                view_count = None
                commentId = None
            else:
                commentId = jmespath.search('commentId.comment_id', COVER_INFO)
                category = category if category \
                    else self.extract_category_from_COVER_INFO(COVER_INFO=COVER_INFO)
                view_count = jmespath.search('positive_view_today_count', COVER_INFO)
                if not view_count or view_count == 'undefined':
                    view_count = jmespath.search('view_today_count', COVER_INFO)
                if not view_count or view_count == 'undefined':
                    view_count = None
        else:
            view_count = selector.css(
                'head meta[itemprop*=interactionCount]::attr(content)').extract_first()
            commentId = None
        if view_count == 'undefined':
            view_count = None

        result = {
            # "webpage_url": webpage_url,
            "vid": vid if vid else re.compile('&vid=(.*?)&').findall(response)[0],
            "title": title,
            "tag": tag.split(',') if tag else None,
            # "from": self.from_,
            "description": selector.css("._video_summary::text").extract_first(),
            "category": ','.join(category) if category else None,
            "cover": 'http://vpic.video.qq.com/0/{vid}.png'.format(vid=vid),
            "upload_ts": upload_ts,
            "duration": duration,
            "view_count": view_count,

        }
        return result, commentId

    @staticmethod
    def extract_category_from_COVER_INFO(COVER_INFO):
        category_map = jmespath.search('category_map', COVER_INFO)
        category = list({ele if isinstance(ele, str) else None for ele in category_map})
        if category:
            if None in category:
                category.remove(None)
            category = ','.join(category)
            return category
        else:
            return None

    @RequestRetry(
        default_exception_return={},
        default_other_exception_return={},
    )
    async def extract_comment_count(self, commentId, session):
        if commentId:
            pass
        else:
            return {}
        headers = {
            'authority': 'video.coral.qq.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
        params = {'source': '0',
                  'targetids': commentId}
        api = 'https://video.coral.qq.com/article/batchcommentnumv2'
        response = await self.request(
            api,
            headers=headers,
            params=params,
            response_type="json",
            session=session
        )
        return {"comment_count": jmespath.search('data[0].commentnum', response)}

    @RequestRetry(
        default_exception_return={},
        default_other_exception_return={},
    )
    async def extract_author_info(self, selector, session):
        user_page_url = selector.css('.video_user a::attr(href)').extract_first()
        if not user_page_url or user_page_url == 'javascript:':
            return {}
        headers = {'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': self.random_ua(),
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
        response = await self.request(
            user_page_url,
            headers=headers,
            session=session
        )
        selector = Selector(text=response)
        result = {
            "author": self.extract_author_name(selector=selector),
            "author_url": user_page_url,
        }
        return result

    @staticmethod
    def extract_author_name(selector):
        author = selector.css('.user_info_name::text').extract_first()
        if author is None:
            author = selector.css('head title::text').extract_first()
            if author:
                return author.replace('的个人频道', '')
        else:
            return author

    @staticmethod
    def strptime(string):
        if string not in {'null', 'undefined'} and string:
            try:
                struct_time = time.strptime(string[:10], '%Y-%m-%d')
            except ValueError:
                try:
                    struct_time = time.strptime(string, '%Y年%m月%d日发布')
                except ValueError:
                    return None, None
            ts = int(time.mktime(struct_time)) if string else None
            upload_date = time.strftime("%Y%m%d", struct_time) if string else None
            return ts, upload_date
        else:
            return None, None

    @staticmethod
    def cal_duration(raw_duration_string):
        regex = re.compile("(\d{1,3})([HMS]?)")
        try:
            _duration = regex.findall(raw_duration_string)
        except TypeError:
            print(f"raw_duration_string: {raw_duration_string}")
            traceback.print_exc()
            return None
        duration = 0
        for value, pointer in _duration:
            if pointer == 'H':
                duration += int(value) * 60 * 60
            elif pointer == 'M':
                duration += int(value) * 60
            elif pointer == 'S':
                duration += int(value)

        return duration if duration else None

    async def extract_by_vkey(self, vid, url, session):
        Host = choice(['vv.video.qq.com', 'tt.video.qq.com', 'flvs.video.qq.com',
                       'tjsa.video.qq.com', 'a10.video.qq.com', 'xyy.video.qq.com', 'vsh.video.qq.com',
                       'vbj.video.qq.com', 'bobo.video.qq.com', 'h5vv.video.qq.com'])
        extract_by_vkey_headers = {'Accept-Encoding': 'gzip, deflate',
                                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                   'User-Agent': self.random_ua(),
                                   'Host': Host,
                                   'Accept': '*/*',
                                   'Cache-Control': 'max-age=0',
                                   'Upgrade-Insecure-Request': '1'}
        guid = self.createGUID()
        extract_by_vkey_params = {'vid': vid,
                                  'platform': 101001,
                                  'otype': 'json',
                                  'guid': guid,
                                  'defaultfmt': 'shd',
                                  'defnpayver': 1,
                                  'appVer': '3.0.83',
                                  'host': 'v.qq.com',
                                  'ehost': url,
                                  'defn': 'mp4',
                                  'fhdswitch': 0,
                                  'show1080p': 1,
                                  'isHLS': 0,
                                  'newplatform': 'v1010',
                                  'defsrc': 1,
                                  'sdtfrom': 'v1010',
                                  '_0': 'undefined',
                                  '_1': 'undefined',
                                  '_2': 'undefined',
                                  '_': int(round(time.time() * 1000)),
                                  'callback': 'QZOutputJson=',
                                  'charge': 0}

        api_get_info = os.path.join('http://', Host, 'getinfo')
        response_getinfo_text = await self.request(
            url=api_get_info,
            session=session,
            headers=extract_by_vkey_headers,
            params=extract_by_vkey_params
        )
        ResJson = json.loads(response_getinfo_text[len('QZOutputJson='):-1])
        filename = jmespath.search('vl.vi[0].fn', ResJson)
        if not filename:
            return False
        else:
            vkey = jmespath.search('vl.vi[0].fvkey', ResJson)
            url_prefix = jmespath.search('vl.vi[0].ul.ui[-1].url', ResJson)
            result = {'play_addr': os.path.join(url_prefix, filename) + '?vkey=' + vkey, 'vid': vid}
            return result

    @staticmethod
    def createGUID():
        length = 32
        guid, position = '', 1
        while length >= position:
            digit = format(math.floor(16 * random.uniform(0, 1)), 'x')
            guid += digit
            position += 1
        return guid

    # @RequestRetry
    # async def extract_by_api(self, url, session):
    #     extract_by_api_headers = {'Accept-Encoding': 'gzip, deflate',
    #                               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #                               'User-Agent': self.random_ua(),
    #                               'Accept': '*/*',
    #                               'Referer': 'http://v.ranks.xin/',
    #                               'X-Requested-With': 'XMLHttpRequest'}
    #     params = {'url': url}
    #     api = 'http://v.ranks.xin/video-parse.php'
    #     async with session.get(api, headers=extract_by_api_headers, params=params) as response:
    #         response_json = await response.json()
    #         play_addr = jmespath.search('data[0].url', response_json)
    #         if not play_addr:
    #             return False
    #         result = {'play_addr': play_addr}
    #         return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
from scrapy.selector import Selector
import emoji
import re
import dateutil.parser
import traceback
import os
from aioVextractor.extractor.tool_set import (
    ToolSet,
    validate,
    RequestRetry
)


class Extractor(ToolSet):
    target_website = [
        "http[s]?://www\.xinpianchang\.com/a\d{7,10}",
        "http[s]?://h5\.xinpianchang\.com/article/index.html\?id=\d{7,10}",
    ]

    TEST_CASE = [
        "https://www.xinpianchang.com/a10475334?from=ArticleList",
        "https://h5.xinpianchang.com/article/index.html?id=10595587",
    ]

    def __init__(self, *args, **kwargs):
        ToolSet.__init__(self, *args, **kwargs)
        self.from_ = "xinpianchang"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        if re.match("http[s]?://h5\.xinpianchang\.com/article/index.html\?id=\d{7,10}", webpage_url):
            vid = re.findall('id=(\d{7,10})', webpage_url)[0]
            webpage_url = f"https://www.xinpianchang.com/a{vid}?from=ArticleList"

        headers = self.general_headers(user_agent=self.random_ua())
        params = {'from': 'ArticleList'}
        response_text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            params=params
        )
        webpage = await self.extract_publish(response=response_text)
        xpc_vid = webpage['vid']
        database_vid = webpage_url.split('?')[0].split('/')[-1].strip('a')
        if not xpc_vid:
            return False
        video = await self.extract_video_info(referer=webpage_url, vid=xpc_vid, session=session)
        if all([webpage, video]):
            return self.merge_dicts(webpage, video, {"vid": database_vid})
        else:
            return False

    async def extract_publish(self, response):
        result = dict()
        try:
            selector = Selector(text=response)
        except:
            traceback.print_exc()
            return False
        vid = selector.css('body script').re_first('vid: "([\s|\S]*?)",')
        # result['from'] = self.from_
        result['vid'] = vid
        try:
            result['author'] = emoji.demojize(selector.css('.creator-info .name::text').extract_first().strip())
        except AttributeError:
            result['author'] = None
        result['author_id'] = selector.css('a[data-userid]::attr(data-userid)').extract_first()
        uploader_url = selector.css('a[data-userid]::attr(href)').extract_first()
        try:
            result['author_url'] = os.path.join("https://www.xinpianchang.com", uploader_url.strip('/'))
        except AttributeError:
            result['author_url'] = None

        result['title'] = selector.css('.title-wrap .title::text').extract_first()
        result['tag'] = selector.css('.tag-wrapper a ::text').extract()  ## ['公益', '央视', '清明']
        try:
            result['category'] = list(map(lambda x: x.strip(), selector.css('.cate a::text').extract()))
        except AttributeError:
            result['category'] = None

        video_create_time = selector.css('meta[property="article:published_time"]::attr(content)').extract_first()
        result['upload_ts'] = int(dateutil.parser.parse(video_create_time).timestamp()) if video_create_time else None

        try:
            result['description'] = self.unescape('\n'.join(
                map(lambda x: x.strip(), selector.css('.filmplay-info-desc>p[class~="desc"]::text').extract())))
        except AttributeError:
            result['description'] = None
        try:
            result['view_count'] = int(selector.css('.play-counts::text').extract_first().replace(',', ''))
        except (ValueError, AttributeError):
            result['view_count'] = None
        try:
            result['like_count'] = int(selector.css('.like-counts::text').extract_first().replace(',', ''))
        except (ValueError, AttributeError):
            result['like_count'] = None
        result['cover'] = selector.css('script').re_first("cover: '([\s|\S]*?)',")
        return result

    @RequestRetry
    async def extract_video_info(self, referer, vid, session):
        headers = {'User-Agent': self.random_ua(),
                   'Referer': referer,
                   'Origin': 'http://www.xinpianchang.com'}
        params = {'expand': 'resource,resource_origin?'}
        extract_video_info_url = f'https://openapi-vtom.vmovier.com/v3/video/{vid}'
        response_json = await self.request(
            url=extract_video_info_url,
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        try:
            play_addr = jmespath.search('max_by(data.resource.progressive, &filesize).https_url', response_json)
        except:
            play_addr = jmespath.search('data.resource.progressive[-1].https_url', response_json)
        duration = jmespath.search('data.video.duration', response_json)
        try:
            width, height = jmespath.search('data.resource.*.[width, height]', response_json)[0]
        except IndexError:
            width = height = None
        result = {
            "play_addr": play_addr,
            "duration": int(int(duration) / 1000) if duration else duration,
            # "webpage_url": referer,
            "width": width,
            "height": height,
        }
        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

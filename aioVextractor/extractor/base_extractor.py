#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/30
# IDE: PyCharm
from aioVextractor.utils import RequestRetry
from scrapy.selector import Selector
import asyncio
import aiohttp
import youtube_dl
import traceback
import jmespath
import time
import os
from concurrent import futures  ## lib for multiprocessing and threading
from aioVextractor.extractor.tencent import Extractor as tencentIE
from aioVextractor.extractor.youku import Extractor as youkuIE
from aioVextractor.extractor.xinpianchang import Extractor as xinpianchangIE
from urllib.parse import (
    urlparse,
)
from aioVextractor.extractor.tool_set import (
    ToolSet,
    validate,
)

from abc import (
    ABCMeta,
    abstractmethod
)


class BaseExtractor(ToolSet, metaclass=ABCMeta):
    """
    When you define a new extractor base on this class
    1. specify target_website as class variable
    2. inherit BaseExtractor.__init__() and define self.from_
    3. redefine BaseExtractor.entracne()
    4. Regenerate file extractor.extractors
    """

    @validate
    @RequestRetry
    @abstractmethod
    def entrance(self, *args, **kwargs):
        pass

    async def extract_iframe(self, iframe_url, session):
        """
        An API to extract iframe with src link to v.qq / youku / youtube / vimeo and etc.
        :param iframe_url:
        :param session:
        :return:
        """
        if 'v.qq.com' in iframe_url:
            with tencentIE() as proxy_extractor:
                return await proxy_extractor.entrance(webpage_url=iframe_url, session=session)
        elif 'player.youku.com' in iframe_url or 'v.youku' in iframe_url:
            with youkuIE() as proxy_extractor:
                return await proxy_extractor.entrance(webpage_url=iframe_url, session=session)
        elif "xinpianchang" in iframe_url:
            with xinpianchangIE() as proxy_extractor:
                return await proxy_extractor.entrance(webpage_url=iframe_url, session=session)
        else:
            return await self.breakdown(webpage_url=iframe_url, session=session)

    async def extract_info(self, webpage_url, collaborate=True):
        """
        Extracting the webpage by youtube-dl without downloading
        :param webpage_url:
        :param collaborate: IGNORE THIS (seems to be useless at this point)
        :return:
        """
        args = {
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            # "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True,
            'user-agent': self.general_headers(user_agent=self.random_ua()),
            "proxy": os.environ.get('HTTP_PROXY', None),
        }
        try:
            with youtube_dl.YoutubeDL(args) as ydl:
                try:
                    VideoJson = ydl.extract_info(webpage_url)
                except:
                    traceback.print_exc()
                    return False
                else:
                    if VideoJson:
                        # if collaborate:
                        #     result = self.extract_single(video_json=VideoJson, webpage_url=webpage_url)
                        #     return result
                        # else:  ## webpage extracting using only youtube-dl
                        if 'entries' in VideoJson:
                            result = []
                            for entry in jmespath.search('entries[]', VideoJson):
                                element = self.extract_single(video_json=entry, webpage_url=webpage_url)
                                result.append(element)
                            return result
                        else:
                            result = self.extract_single(video_json=VideoJson, webpage_url=webpage_url)
                            return [result]
                    else:
                        return False
        except:
            traceback.print_exc()
            return False

    def extract_single(self, video_json, webpage_url):
        """
        scrubbing info from video_json which comes from youtube-dl output
        :param video_json:
        :param webpage_url:
        :return:
        """
        result = dict()
        result['downloader'] = 'ytd'
        result['webpage_url'] = webpage_url
        result['author'] = jmespath.search('uploader', video_json)
        result['cover'] = self.check_cover(jmespath.search('thumbnail', video_json))
        create_time = jmespath.search('upload_date', video_json)
        upload_ts = int(time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
        result['upload_ts'] = upload_ts
        result['description'] = jmespath.search('description', video_json)
        duration = jmespath.search('duration', video_json)
        result['duration'] = int(duration) if duration else 0
        result['rating'] = jmespath.search('average_rating', video_json)
        result['height'] = jmespath.search('height', video_json)
        result['like_count'] = jmespath.search('like_count', video_json)
        result['view_count'] = jmespath.search('view_count', video_json)
        result['dislike_count'] = jmespath.search('dislike_count', video_json)
        result['width'] = jmespath.search('width', video_json)
        result['vid'] = jmespath.search('id', video_json)
        cate = jmespath.search('categories', video_json)
        result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) \
            if cate \
            else cate
        # formats = self.extract_play_addr(VideoJson)
        # result['play_addr'] = formats['url']
        result['from'] = video_json.get('extractor', None).lower() \
            if video_json.get('extractor', None) \
            else urlparse(webpage_url).netloc
        result['title'] = jmespath.search('title', video_json)
        video_tags = jmespath.search('tags', video_json)
        result['tag'] = video_tags
        return result

    @staticmethod
    def extract_play_addr(video_json):
        """

        This method is depreciated

        extract play_addr from the return of youtube-dl
        :param video_json:
        :return:
        """
        video_list = jmespath.search('formats[]', video_json)
        try:
            try:
                return sorted(filter(
                    lambda x: (x.get('protocol', '') in {'https', 'http'}) and x.get('acodec') != 'none' and x.get(
                        'vcodec') != 'none', video_list), key=lambda x: x['filesize'])[-1]
            except KeyError:
                return sorted(filter(
                    lambda x: x.get('protocol', '') in {'https', 'http'} and x.get('acodec') != 'none' and x.get(
                        'vcodec') != 'none', video_list), key=lambda x: x['height'])[-1]
            except IndexError:
                return jmespath.search('formats[-1]', video_json)
        except:
            return jmespath.search('formats[-1]', video_json)

    @RequestRetry
    async def retrieve_webpapge(self, webpage_url):
        """
        retrieve webpage
        """
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(webpage_url, headers=self.general_headers(self.random_ua())) as response:
                return await response.text()

    async def breakdown(self, webpage_url, session):
        """
        extract iframes from webpage_url and extract these iframe_urls concurrently
        :return:
        """

        def wrapper(url):
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                r = new_loop.run_until_complete(self.extract_info(webpage_url=url, collaborate=False))
                new_loop.close()
                return r
            except:
                traceback.print_exc()
                return False

        webpage_content = await self.request(
            url=webpage_url,
            session=session,
            headers=self.general_headers(user_agent=self.random_ua())
        )
        try:
            selector = Selector(text=webpage_content)
        except TypeError:
            return False
        iframe_src = selector.css('iframe::attr(src)').extract()
        with futures.ThreadPoolExecutor(max_workers=min(10, os.cpu_count())) as executor:  ## set up processes
            executor.submit(wrapper)
            future_to_url = [executor.submit(wrapper, url=iframe) for iframe in iframe_src]
            results = []
            try:
                for f in futures.as_completed(future_to_url, timeout=max([len(iframe_src) * 3, 15])):
                    try:
                        result = f.result()
                        for ele in result:
                            ele['playlist_url'] = webpage_url
                            results.append(ele)
                    except:
                        traceback.print_exc()
                        continue
            except:
                traceback.print_exc()
                pass
            return results


if __name__ == '__main__':
    from pprint import pprint

    with BaseExtractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/55684.html")
        pprint(res)
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/56636.html")
        pprint(res)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from aioVextractor.utils.user_agent import safari
from random import choice
from urllib.parse import (urlsplit, unquote)
import jmespath
import emoji
import traceback
import re
import html
from aioVextractor.utils import RequestRetry
import platform
from scrapy import Selector
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://www\.youtube\.com/channel/[\w-]{10,36}",
        "http[s]?://www\.youtube\.com/playlist\?list=[\w-]{10,36}",
        "http[s]?://www\.youtube\.com/user.*",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://www.youtube.com/channel/UCSRpCBq2xomj7Sz0od73jWw/videos",
        "https://www.youtube.com/channel/UCAyj5vEhoaw6fDFBpSbQvRg",
        "https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc",
        "https://www.youtube.com/user/ShortoftheWeek/videos",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "youtube"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        ParseResult = urlsplit(webpage_url)
        path = ParseResult.path
        page = int(kwargs.pop("page", 1))
        if re.match('/playlist', path):
            if page > 1:
                webpage_content = await self.retrieve_youtube_pageing_api(
                    referer=webpage_url,
                    continuation=kwargs['continuation'],
                    clickTrackingParams=kwargs['clickTrackingParams'],
                    session=session
                )

                results = await self.extract_youtube_pageing_api(
                    ResJson=webpage_content,
                    path='playlist',
                    webpage_url=webpage_url)
                return results
            else:
                headers = {'authority': 'www.youtube.com',
                           'upgrade-insecure-requests': '1',
                           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                           'accept-encoding': 'gzip, deflate, br',
                           'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                           }
                webpage_content = await self.request(
                    url=webpage_url,
                    session=session,
                    headers=headers
                )

                results = await self.extract_webpage(webpage_content, webpage_url=webpage_url, path='playlist')
                return results

        elif re.match('/channel/', path) or re.match('/user/', path):
            if page > 1:
                webpage_content = await self.retrieve_youtube_pageing_api(
                    referer=webpage_url,
                    continuation=kwargs['continuation'],
                    clickTrackingParams=kwargs['clickTrackingParams'],
                    session=session
                )
                results = await self.extract_youtube_pageing_api(ResJson=webpage_content, webpage_url=webpage_url,
                                                                 path='channel')
                return results
            else:
                webpage_url += '' if webpage_url.endswith('/videos') else '/videos'
                headers = {'authority': 'www.youtube.com',
                           'upgrade-insecure-requests': '1',
                           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                           'accept-encoding': 'gzip, deflate, br',
                           'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                           }
                webpage_content = await self.request(
                    url=webpage_url,
                    session=session,
                    headers=headers
                )
                results = await self.extract_webpage(webpage_content, webpage_url=webpage_url, path='channel')
                return results

    async def retrieve_youtube_pageing_api(self, referer, continuation, clickTrackingParams, session):
        """
        retrieve next page response.
        each response contains 100 element at most.
        continuation and clickTrackingParams aRre retrieved from ytInitialData.
        """
        headers = {'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   'x-spf-referer': referer,
                   'x-spf-previous': referer,
                   'x-youtube-client-version': '2.20190702',
                   'user-agent': choice(safari),
                   'accept': '*/*',
                   'referer': referer,
                   'x-youtube-client-name': '1',
                   'authority': 'www.youtube.com',
                   }

        params = {'ctoken': continuation,
                  'continuation': continuation,
                  'itct': clickTrackingParams,
                  }
        response = await self.request(
            url='https://www.youtube.com/browse_ajax',
            session=session,
            headers=headers,
            params=params,
            response_type="json"
        )
        return response

    async def extract_youtube_pageing_api(self, ResJson, webpage_url, path='playlist'):
        """
        extract playlist webpage by extracting ytInitialData
        yield each element and follow by (continuation, clickTrackingParams) at last
        """
        ytInitialData = ResJson
        # print(ytInitialData)
        if path == 'playlist':
            statement = '[1].' \
                        'response.' \
                        'continuationContents.' \
                        'playlistVideoListContinuation.' \
                        'contents[].playlistVideoRenderer.{' \
                        '"duration": lengthSeconds, ' \
                        '"view_count": viewCountText.simpleText, ' \
                        '"vid": videoId, ' \
                        '"cover": thumbnail.thumbnails[-1].url, ' \
                        '"title": title.simpleText, ' \
                        '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                        '}'
            results = jmespath.search(statement, ytInitialData)
        else:  ## path == 'channel'
            statement = '[1].' \
                        'response.' \
                        'continuationContents.' \
                        'gridContinuation.' \
                        'items[].gridVideoRenderer.{' \
                        '"view_count": viewCountText.simpleText, ' \
                        '"vid": videoId, ' \
                        '"cover": thumbnail.thumbnails[-1].url, ' \
                        '"title": title.simpleText, ' \
                        '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                        '}'
            results = jmespath.search(statement, ytInitialData)
            if results is None:
                statement = 'response.' \
                            'continuationContents.' \
                            'gridContinuation.' \
                            'items[].gridVideoRenderer.{' \
                            '"view_count": viewCountText.simpleText, ' \
                            '"vid": videoId, ' \
                            '"cover": thumbnail.thumbnails[-1].url, ' \
                            '"title": title.simpleText, ' \
                            '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                            '}'
                results = jmespath.search(statement, ytInitialData)
        if isinstance(results, list):
            pass
        else:
            return None
        output = []
        for ele in results:
            try:
                title = emoji.demojize(unquote(html.unescape(ele['title'])))
            except TypeError:
                traceback.print_exc()
                title = None
                pass
            result = {
                "vid": ele['vid'],
                "cover": ele['cover'],
                "title": title,
                "playlist_url": webpage_url,
                "from": self.from_,
                "view_count": ele['view_count'].replace(',', '').replace(' 次观看', '') if ele['view_count'] else None,
                "webpage_url": 'https://www.youtube.com' + ele['webpage_url'],
            }
            output.append(result)
        else:
            if path == 'playlist':
                statement = '[1].' \
                            'response.' \
                            'continuationContents.' \
                            'playlistVideoListContinuation.' \
                            'continuations[0].' \
                            'nextContinuationData.' \
                            '[continuation, clickTrackingParams]'
            else:  ## path == 'channel'
                statement = '[1].' \
                            'response.' \
                            'continuationContents.' \
                            'gridContinuation.' \
                            'continuations[0].' \
                            'nextContinuationData.' \
                            '[continuation, clickTrackingParams]'
            try:
                continuation, clickTrackingParams = jmespath.search(statement, ytInitialData)
            except TypeError:  ## cannot unpack non-iterable NoneType object
                return output, False, {}
            else:
                return output, True, {"continuation": continuation, "clickTrackingParams": clickTrackingParams}

    async def extract_webpage(self, ResText, webpage_url, path='playlist'):
        """
        extract playlist webpage by extracting ytInitialData
        yield each element and follow by (continuation, clickTrackingParams) at last
        """
        try:
            selector = Selector(text=ResText)
        except ValueError:
            traceback.print_exc()
            return None  ## None is returned
        else:
            try:
                try:
                    ytInitialData = json.loads(
                        json.loads(selector.css('script').
                                   re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
                except TypeError:
                    ytInitialData = json.loads(
                        selector.css('script').
                            re_first(
                            'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
            except TypeError:
                traceback.print_exc()
                return None  ## None is returned
            # print(ytInitialData)
            else:
                if path == 'playlist':
                    statement = 'contents.' \
                                'twoColumnBrowseResultsRenderer.' \
                                'tabs[0].' \
                                'tabRenderer.' \
                                'content.' \
                                'sectionListRenderer.' \
                                'contents[0].' \
                                'itemSectionRenderer.' \
                                'contents[0].' \
                                'playlistVideoListRenderer.' \
                                'contents[].playlistVideoRenderer.{' \
                                '"duration": lengthSeconds, ' \
                                '"vid": videoId, ' \
                                '"cover": thumbnail.thumbnails[-1].url, ' \
                                '"title": title.simpleText, ' \
                                '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                                '}'
                    results = jmespath.search(statement, ytInitialData)
                else:  ## path == 'channel':
                    statement = 'contents.' \
                                'twoColumnBrowseResultsRenderer.' \
                                'tabs[1].' \
                                'tabRenderer.' \
                                'content.' \
                                'sectionListRenderer.' \
                                'contents[0].' \
                                'itemSectionRenderer.' \
                                'contents[0].' \
                                'gridRenderer.' \
                                'items[].gridVideoRenderer.{' \
                                '"vid": videoId, ' \
                                '"cover": thumbnail.thumbnails[-1].url, ' \
                                '"title": title.simpleText, ' \
                                '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                                '}'
                    results = jmespath.search(statement, ytInitialData)
                    if results is None:
                        statement = 'contents.' \
                                    'twoColumnBrowseResultsRenderer.' \
                                    'tabs[0].' \
                                    'tabRenderer.' \
                                    'content.' \
                                    'sectionListRenderer.' \
                                    'contents[0].' \
                                    'itemSectionRenderer.' \
                                    'contents[0].' \
                                    'shelfRenderer.' \
                                    'content.' \
                                    'horizontalListRenderer.' \
                                    'items[].gridVideoRenderer.{' \
                                    '"vid": videoId, ' \
                                    '"cover": thumbnail.thumbnails[-1].url, ' \
                                    '"title": title.simpleText, ' \
                                    '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                                    '}'
                        results = jmespath.search(statement, ytInitialData)
                if results is None:
                    print(f"Cannot extract ytInitialData: {ytInitialData}")
                    return None
                output = []
                for ele in results:
                    try:
                        title = unquote(html.unescape(ele['title']))
                    except TypeError:
                        title = None
                    result = {
                        "vid": ele['vid'],
                        "cover": ele['cover'],
                        "title": title,
                        "playlist_url": webpage_url,
                        "from": self.from_,
                        "webpage_url": 'https://www.youtube.com' + ele['webpage_url'],
                    }
                    output.append(result)
                else:
                    if path == 'playlist':
                        statement = 'contents.' \
                                    'twoColumnBrowseResultsRenderer.' \
                                    'tabs[0].' \
                                    'tabRenderer.' \
                                    'content.' \
                                    'sectionListRenderer.' \
                                    'contents[0].' \
                                    'itemSectionRenderer.' \
                                    'contents[0].' \
                                    'playlistVideoListRenderer.' \
                                    'continuations[0].' \
                                    'nextContinuationData.' \
                                    '[continuation, clickTrackingParams]'
                    else:  ## path == 'channel':
                        statement = 'contents.' \
                                    'twoColumnBrowseResultsRenderer.' \
                                    'tabs[1].' \
                                    'tabRenderer.' \
                                    'content.' \
                                    'sectionListRenderer.' \
                                    'contents[0].' \
                                    'itemSectionRenderer.' \
                                    'contents[0].' \
                                    'gridRenderer.' \
                                    'continuations[0].' \
                                    'nextContinuationData.' \
                                    '[continuation, clickTrackingParams]'
                        result = jmespath.search(statement, ytInitialData)
                        if result is None:
                            statement = 'contents.' \
                                        'twoColumnBrowseResultsRenderer.' \
                                        'tabs[0].' \
                                        'tabRenderer.' \
                                        'content.' \
                                        'sectionListRenderer.' \
                                        'contents[0].' \
                                        'itemSectionRenderer.' \
                                        'contents[0].' \
                                        'shelfRenderer.' \
                                        'content.' \
                                        'horizontalListRenderer.' \
                                        'continuations[0].' \
                                        'nextContinuationData.' \
                                        '[continuation, clickTrackingParams]'

                    try:
                        continuation, clickTrackingParams = jmespath.search(statement, ytInitialData)
                    except TypeError:  ## cannot unpack non-iterable NoneType object\
                        return output, False, {}
                    else:
                        return output, True, {"continuation": continuation, "clickTrackingParams": clickTrackingParams}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # params={'clickTrackingParams': 'CDwQybcCIhMI0rC0jdi05QIVlxxgCh23ZQF8',
            #         'continuation': '4qmFsgI0EhhVQ1NScENCcTJ4b21qN1N6MG9kNzNqV3caGEVnWjJhV1JsYjNNZ0FEZ0JlZ0V5dUFFQQ%3D%3D'}
        )
        pprint(res)

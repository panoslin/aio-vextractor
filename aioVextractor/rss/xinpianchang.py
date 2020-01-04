#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from aioVextractor.rss import (
    RssValidater,
    BaseRss,
)
from scrapy import Selector


class Rss(BaseRss):
    # target_website = [
    #     "https://space\.bilibili\.com/\d{5,10}",
    # ]

    # downloader = 'ytd'

    # TEST_CASE = [
    #     "https://space.bilibili.com/29296192/video",
    # ]

    def __init__(self, *args, **kwargs):
        BaseRss.__init__(self, *args, **kwargs)
        self.from_ = "xinpianchang"

    @RssValidater
    async def fetch(self, session, page=1, *args, **kwargs):
        headers = {
            'authority': 'www.xinpianchang.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'referer': 'https://www.xinpianchang.com/channel/index/sort-like?from=tabArticle',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}

        params = {'from': 'articleListPage'}

        api = f'https://www.xinpianchang.com/channel/index/type-/sort-addtime/duration_type-0/resolution_type-/page-{page}'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params
        )
        return self.extract(text=response, playlist_url=api)

    # async def request_page(self, session, page=1):
    #     headers = {
    #         'authority': 'www.xinpianchang.com',
    #         'cache-control': 'max-age=0',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': self.random_ua(),
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    #         'referer': 'https://www.xinpianchang.com/channel/index/sort-like?from=tabArticle',
    #         'accept-encoding': 'gzip, deflate, br',
    #         'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
    #
    #     params = {'from': 'articleListPage'}
    #
    #     api = f'https://www.xinpianchang.com/channel/index/type-/sort-addtime/duration_type-0/resolution_type-/page-{page}'
    #     return await self.request(
    #         url=api,
    #         session=session,
    #         headers=headers,
    #         params=params
    #     )
    #     async with session.get(api, headers=headers, params=params) as response:
    #         return await response.text()

    def extract(self, text, playlist_url):
        results = []
        sel = Selector(text=text)
        for li in sel.css('li[data-articleid]'):
            result = dict()
            result['playlist_url'] = playlist_url
            result['vid'] = li.css('li::attr(data-articleid)').extract_first()
            result['cover'] = li.css('a[class*="video-cover"] img::attr(_src)').re_first('(http[\s|\S]*?)@')
            result['title'] = li.css('div[class*="video-con"] p::text').extract_first()
            result['duration'] = self.string2duration(
                string=li.css('span[class*="duration"]::text').extract_first(),
                format="%M' %S''"
            )

            category = li.css('.new-cate span[class*="fs_"]::text').extract()
            result['category'] = ",".join(list(map(lambda x: x.strip(), category))) if category else None

            author = li.css('div[class*="user-info"] span[class*="name"]::text').extract_first()

            try:
                if '位创作人' in author:
                    author = li.css('.authors-wrap .authors-list .info .name::text').extract_first()
            except TypeError:
                pass
            result['author'] = author.strip() if author else None

            role = li.css('div[class*="user-info"] span[class*="role"]::text').extract_first()
            result['role'] = role.strip() if role else None
            result['author_id'] = li.css('a[data-userid]::attr(data-userid)').extract_first()
            result['author_url'] = f"https://www.xinpianchang.com/u{result['author_id']}"
            result['view_count'] = li.css('.icon-play-volume::text').extract_first()
            result['like_count'] = li.css('.icon-like::text').extract_first()
            result['recommend'] = self.format_recommend(
                li.css('.video-mark span[class*="pick"]::attr(class)').extract_first()
            )
            result['webpage_url'] = f"https://www.xinpianchang.com/a{result['vid']}"
            # result['upload_ts'] = self.format_upload_ts(    li.css('.video-hover-con p[class*="fs_12"]::text').extract_first())
            result['upload_ts'] = self.string2timestamp(
                string=li.css('.video-hover-con p[class*="fs_12"]::text').extract_first(),
                format='%Y-%m-%d 发布'
            )

            result['from'] = self.from_
            # result['database_status'] = False
            results.append(result)
        return results

    @staticmethod
    def format_recommend(recommend):
        """
        input: 'pick vmovier'
        """
        if recommend == 'pick vmovier':
            return "PickComposer"
        elif recommend == 'pick square':
            return "PickVideo"
        else:
            return recommend


if __name__ == '__main__':
    from pprint import pprint

    with Rss() as rss:
        res = rss.sync_fetch(
        )
        pprint(res)

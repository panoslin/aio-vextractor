#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import traceback
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from lxml import etree


class Breaker(BaseBreaker):
    target_website = [
        "https://www.topys.cn/category/\d{1,2}\.\w{4}",
    ]

    TEST_CASE = [
        "https://www.topys.cn/category/7.html",
        "https://www.topys.cn/category/12.html",
        "https://www.topys.cn/category/8.html",
        "https://www.topys.cn/category/11.html",
        "https://www.topys.cn/category/10.html",
        "https://www.topys.cn/category/9.html",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "topys"

    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.108 Safari/537.36',
            'cookie': 'can_webp=true; '
                      'PHPSESSID=raq083vn8a5sm4ltppn2mnjai4; '
                      'c__utmc=240399687.1533698397; '
                      '_ga=GA1.2.7487009.1576462014; '
                      '_gid=GA1.2.557173347.1576462014; '
                      'can_webp=true; '
                      'c__utma=240399687.1533698397.7484774608419108883.1576486627.1576491436.5; '
                      'c__utmb=240399687.1533698397.1576491436.1576491830.6; '
                      '_gat_UA-106081907-1=1'}
        mes = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )
        soup = etree.HTML(mes)
        token = soup.xpath('//li[@id="login-vue"]/@data-token')[0].encode().decode()
        timestape = soup.xpath('//li[@id="login-vue"]/@data-timestape')[0].encode().decode()
        data_column = soup.xpath('//div[@id="article-list-vue"]/@data-column')[0].encode().decode()
        headers = {
            'authority': 'www.topys.cn',
            'origin': 'https://www.topys.cn',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.108 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': f'PHPSESSID=raq083vn8a5sm4ltppn2mnjai4; '
                      f'c__utmc=240399687.1533698397; '
                      f'_ga=GA1.2.7487009.1576462014; '
                      f'_gid=GA1.2.557173347.1576462014; '
                      f'can_webp=true; '
                      f'c__utma=240399687.1533698397.7484774608419108883.1576486627.1576491436.5; '
                      f'c__utmb=240399687.1533698397.1576491436.{timestape}.7',
        }
        data = {
            'needloginpage': '2',
            'islogin': '0',
            'module': 'article',
            'column': str(data_column),
            'timestape': timestape,
            'token': str(token),
            'offset': '0',
            'size': '12',
            'page': str(page),
            'type': 'column',
            'need_count': 'true'
        }
        api = 'https://www.topys.cn/ajax/article/get_article_list'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            data=data,
            response_type="json",
            method="post"
        )
        results = self.extract(response=response, url=webpage_url, page=page)
        return results

    def extract(self, response, url, page):
        results = []
        data = jmespath.search("result", response)
        count = int(response["count"])
        max_page = count // len(data) + 1
        for ele in data:
            try:
                results.append({
                    "vid": ele['id'],
                    "cover": ele['thumb'],
                    "title": ele['title'],
                    "author": ele['editor'],
                    "tag": ele['keyword'],
                    "from": self.from_,
                    "playlist_url": url,
                    "webpage_url": 'https://www.topys.cn/article/' + ele['id'] + '.html',
                    "view_count": ele["view_count"],
                    "comment_count": ele["comment"],
                    "upload_ts": ele["add_time"],
                    "category": ele["cname"],

                })
            except:
                continue
        else:
            return results, page < max_page, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)

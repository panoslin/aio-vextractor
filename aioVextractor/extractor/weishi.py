#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import jmespath


class Extractor(BaseExtractor):
    target_website = [
        "http[s]://h5.weishi.qq.com/weishi/feed/.*",
    ]

    TEST_CASE = [
        "https://h5.weishi.qq.com/weishi/feed/773iEsW8D1IFFnaYd/wsfeed?wxplay=1&id=773iEsW8D1IFFnaYd&spid=7923282523404242944&qua=v1_and_weishi_6.2.0_588_312027000_d&chid=100081014&pkg=3670&attach=cp_reserves3_1000370011",
        "https://h5.weishi.qq.com/weishi/feed/75MTP2KCr1IDu3Lsp/wsfeed?wxplay=1&id=75MTP2KCr1IDu3Lsp&spid=7923282523404242944&qua=v1_and_weishi_6.2.0_588_312027000_d&chid=100081014&pkg=3670&attach=cp_reserves3_1000370011",
        "https://h5.weishi.qq.com/weishi/feed/76Q1IavTw1IDWbSSt/wsfeed?wxplay=1&id=76Q1IavTw1IDWbSSt&spid=7923282523404242944&qua=v1_and_weishi_6.2.0_588_312027000_d&chid=100081014&pkg=3670&attach=cp_reserves3_1000370011",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weishi"
        self.results = []

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        feedid = webpage_url.split('/')[5]
        data = '{"feedid":"%s","recommendtype":0,"datalvl":"all","_weishi_mapExt":{}}' % str(feedid)
        headers = {
            'authority': 'h5.weishi.qq.com',
            'accept': 'application/json',
            'origin': 'https://h5.weishi.qq.com',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'content-type': 'application/json',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': webpage_url + '&from=pc&orifrom=',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'pgv_pvi=3875408896; pgv_si=s3355604992; pgv_info=ssid=s5924370020; pgv_pvid=7915709504; ptisp=ctc; RK=CipcjFKNEz; ptcz=f6d402e9c10789384eb364aa9dda176d3c1dc11499f9ad63f6da78b7567e6e11; tvfe_boss_uuid=23916d936281ff69; person_id_bak=5402775600267626; person_id_wsbeacon=5739999946119313; wsreq_logseq=317361204',
        }
        params = (
            ('t', '0.9467193756973742'),
            ('g_tk', ''),
        )
        api = 'https://h5.weishi.qq.com/webapp/json/weishi/WSH5GetPlayPage'
        response = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            data=data,
            method='post',
            response_type='json'
        )
        self.extract(response_json=response)
        return self.results

    def extract(self, response_json):
        result = {
            'play_addr': jmespath.search('data.feeds[0].video_url', response_json),
            'title': jmespath.search('data.feeds[0].feed_desc_withat', response_json),
            'comment_count': jmespath.search('data.feeds[0].total_comment_num', response_json),
            'like_count': jmespath.search('data.feeds[0].ding_count', response_json),
            'vid': jmespath.search('data.feeds[0].id', response_json),
            'cover': jmespath.search('data.feeds[0].extern_info.mpEx.feed_cover', response_json),
        }

        self.results.append(result)


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

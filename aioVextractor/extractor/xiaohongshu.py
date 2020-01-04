#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from scrapy import Selector
import os
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://xhsurl\.com/\w{5}",
        "http[s]?://www.xiaohongshu\.com/discovery/item/.*",
    ]

    TEST_CASE = [
        "http://xhsurl.com/3umNO",
        "https://www.xiaohongshu.com/discovery/item/5dea1545000000000100530b?xhsshare=CopyLink&appuid=5dd37f3c0000000001008b0b&apptime=1575963315",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "xiaohongshu"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = {
            'authority': 'www.xiaohongshu.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        if 'https://www.xiaohongshu.com/discovery/item' in webpage_url:
            location = webpage_url
        else:
            response = await self.request(
                url=webpage_url,
                session=session,
                headers=headers,
                allow_redirects=False,
                response_type="raw"
            )
            location = response.headers['Location']
        # response = await self.request(
        #     url=webpage_url,
        #     session=session,
        #     headers=headers,
        #     response_type="raw"
        # )
        # cookie = ''
        # for ele in response.raw_headers:
        #     print(ele[0].decode(), ele[1].decode())
        #     if "Set-Cookie" == ele[0].decode():
        #         cookie += ele[1].decode().replace("Path=/", "")
        # cookie = response.headers['Set-Cookie']
        # headers['cookie'] = cookie
        # cookie = {ele.split("=", 1)[0]: ele.split("=", 1)[1] for ele in cookie.strip("; ").split("; ")}
        # cookie.pop("Max-Age", None)
        # cookie.pop("Domain", None)

        cookie = {
            'xhsTracker': 'url=/discovery/item/5dbd317b000000000100a5fe&xhsshare=CopyLink',
            'xhsTrackerId': 'b4eebbba-74f3-4f9b-cfb4-4d5059963ff2',
            'extra_exp_ids': '',
            'timestamp1': '2322974232',
            'timestamp2': '3854455932',
            'hasaki': '%5B%22Mozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F74.0.3729.108%20Safari%2F537.36%22%2C%22zh-CN%22%2C24%2C-480%2Ctrue%2Ctrue%2Ctrue%2C%22undefined%22%2C%22function%22%2Cnull%2C%22Linux%20x86_64%22%2C6%2C8%2Cnull%2C%22Chrome%20PDF%20Plugin%3A%3APortable%20Document%20Format%3A%3Aapplication%2Fx-google-chrome-pdf~pdf%3BChrome%20PDF%20Viewer%3A%3A%3A%3Aapplication%2Fpdf~pdf%3BNative%20Client%3A%3A%3A%3Aapplication%2Fx-nacl~%2Capplication%2Fx-pnacl~%22%5D',
        }
        response = await self.request(
            url=location,
            session=session,
            headers=headers,
            cookies=cookie,
        )

        results = self.extract(
            response=response,
        )
        return results
        # browser = await self.launch_browers()
        # page = await browser.newPage()
        # await page.goto(webpage_url)
        # await asyncio.sleep(3)
        # response = await page.content()
        # await browser.close()
        # results = self.extract(
        #     response=response,
        #     webpage_url=webpage_url
        # )
        # return results

    def extract(self, response):
        result = dict()
        # result['from'] = self.from_
        selector = Selector(text=response)
        # result['webpage_url'] = webpage_url
        result['title'] = selector.css(".title::text").extract_first()
        try:
            result['author'] = selector.css(".nickname a::text").extract_first().strip()
        except:
            pass

        result['author_avatar'] = selector.css(".author-info img ::attr(src)").extract_first()
        result['upload_ts'] = self.string2timestamp(
            string=selector.css(".publish-date span::text").extract_first(),
            format="发布于 %Y-%m-%d %H:%M"
        )
        try:
            result['description'] = "\n".join(selector.css(".note .content")[0].css("p::text").extract())
        except:
            pass
        result['play_addr'] = selector.css("video::attr(src)").extract_first()
        result['vid'] = result['play_addr'].split("?")[0].split("/")[-1]
        result['cover'] = os.path.join("http://", selector.css(".video-poster::attr(src)").extract_first().lstrip("//"))
        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

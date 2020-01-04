#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

# import jmespath
import re
import requests
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://v\.douyin\.com/[\w\d]{3,9}",
        "http[s]?://www\.iesdouyin\.com/share/video/\d{15,25}/.*?mid=\d{15,25}",
    ]

    TEST_CASE = [
        "#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢 睡姿也太可爱了8#猫 http://v.douyin.com/hd9sb3/ 复制此链接，打开【抖音短视频】，直接观看视频！",
        "http://v.douyin.com/hd9sb3/",
        "https://www.iesdouyin.com/share/video/6759299526001052940/?region=CN&mid=6759299526001052940",
        "http://v.douyin.com/Q3bqGN/",
        "#在抖音，记录美好生活#【60秒】讲拍摄的颜色对比#电影小丑#颜色对比#潮色#2019流行的颜色#小丑 https://v.douyin.com/C5qw3u/ 复制此链接，打开【抖音短视频】，直接观看视频！",
        "https://www.iesdouyin.com/share/video/6747454338836319499/?region=CN&mid=6747444279183936264&u_code=-1&titleType=",  ## link expired
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "douyin"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        browser = await self.launch_browers()
        # browser = await launch(args=['--no-sandbox'])
        page = await browser.newPage()
        await page.goto(webpage_url)
        response_text = await page.content()
        results = self.extract_page(response=response_text, page=page)
        await browser.close()
        return results

        # download_headers = {'Connection': 'keep-alive',
        #                     'Upgrade-Insecure-Requests': '1',
        #                     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        #                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #                     'Accept-Encoding': 'gzip, deflate',
        #                     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
        # async with session.get(webpage_url, headers=download_headers, allow_redirects=False) as response_getinfo:
        #     Location = response_getinfo.headers['Location']
        #     get_aweme_id = lambda location: urlparse(location).path.strip('/').split('/')[-1]
        #     aweme_id = get_aweme_id(Location)
        #     # print(f"aweme_id: {aweme_id}")
        #     result = self.extract(response_json=await self.aweme_detail(aweme_id=aweme_id,
        #                                                                 session=session))
        #
        #     return result if result else False

    # @RequestRetry
    # async def aweme_detail(self, aweme_id, session):
    #     """
    #     get all info of the video
    #     """
    #     api = f'https://aweme-hl.snssdk.com/aweme/v1/aweme/detail/?aweme_id={aweme_id}&device_platform=ios&app_name=aweme&aid=1128'
    #     aweme_detail_headers = {'user-agent': 'Mozilla/5.0'}
    #
    #     response = await self.request(
    #         url=api,
    #         session=session,
    #         headers=aweme_detail_headers,
    #         response_type="json"
    #     )
    #
    #     return jmespath.search('aweme_detail', response)

    # @staticmethod
    # def extract(response_json):
    #     """
    #     extract all info from response_json
    #     """
    #     if response_json is False:
    #         return False
    #     else:
    #         result = dict()
    #         # result['from'] = self.from_
    #         result['author'] = jmespath.search('author.nickname', response_json)
    #         result['author_avatar'] = jmespath.search('author.avatar_larger.url_list[0]', response_json)
    #         result['author_description'] = jmespath.search('author.signature', response_json)
    #         author_gender = jmespath.search('author.gender', response_json)
    #         if author_gender == 2:
    #             result['author_gender'] = '女'
    #         elif author_gender == 1:
    #             result['author_gender'] = '男'
    #         else:
    #             result['author_gender'] = None
    #         result['author_id'] = jmespath.search('author.uid', response_json)
    #         result['play_addr'] = jmespath.search("video.play_addr.url_list[?contains(@, 'bytecdn')] | [0]",
    #                                               response_json)
    #         if not result['play_addr']:
    #             result['play_addr'] = jmespath.search("video.play_addr.url_list[0]", response_json)
    #         if not result['play_addr']:
    #             return False
    #         result['title'] = jmespath.search('desc', response_json)
    #         result['vid'] = jmespath.search('aweme_id', response_json)
    #         result['cover'] = jmespath.search('video.cover.url_list[0]', response_json)
    #         result['tag'] = jmespath.search('text_extra[].hashtag_name', response_json)
    #         result['language'] = jmespath.search('desc_language', response_json)
    #         result['region'] = jmespath.search('region', response_json)
    #         result['upload_ts'] = jmespath.search('create_time', response_json)
    #         # result['webpage_url'] = jmespath.search('share_url', response_json)
    #         result['comment_count'] = jmespath.search('statistics.comment_count', response_json)
    #         result['like_count'] = jmespath.search('statistics.digg_count', response_json)
    #         result['download_count'] = jmespath.search('statistics.download_count', response_json)
    #         result['forward_count'] = jmespath.search('statistics.forward_count', response_json)
    #         result['share_count'] = jmespath.search('statistics.share_count', response_json)
    #         result['height'] = jmespath.search('video.height', response_json)
    #         result['width'] = jmespath.search('video.width', response_json)
    #         video_duration = jmespath.search('video.duration', response_json)
    #         result['duration'] = int(int(video_duration) / 1000) if video_duration else None
    #         return result

    def extract_page(self, response, page):
        selector = self.Selector(text=response)
        result = dict()
        # result['from'] = self.from_
        result['author'] = selector.css(".detail .user-info .name::text").extract_first().lstrip("@")
        result['author_avatar'] = selector.css(".detail .user-info img::attr(src)").extract_first()
        result['play_addr'] = self.redirect_play_addr(
            selector.css("script").re_first('playAddr: "([\s|\S]*?)"').replace("playwm", "play"))
        result['title'] = selector.css(".desc::text").extract_first()
        result['vid'] = re.findall("\d{15,21}", page.url)[0]
        result['cover'] = selector.css("script").re_first('cover: "([\s|\S]*?)"')
        result['tag'] = selector.css(".inner::text").extract()
        # result['webpage_url'] = page.url
        result['height'] = selector.css("script").re_first('videoHeight: ([\s|\S]*?),')
        result['width'] = selector.css("script").re_first('videoWidth: ([\s|\S]*?),')
        return result

    @staticmethod
    @RequestRetry(
        default_exception_return=False,
        default_other_exception_return=False
    )
    def redirect_play_addr(play_addr):
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }
        response = requests.get(play_addr,
                                allow_redirects=False,
                                # headers=self.general_headers(user_agent=self.random_ua())
                                headers=headers
                                )
        return response.headers['Location']


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

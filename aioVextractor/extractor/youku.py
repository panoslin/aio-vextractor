#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import traceback
import time, json
import jmespath
from scrapy import Selector
import asyncio
from aioVextractor.extractor.tool_set import (
    ToolSet,
    validate,
    RequestRetry
)


class Extractor(ToolSet):
    target_website = [
        "http[s]?://v\.youku\.com/v_show/id_\w{10,36}",
        "http[s]?://player\.youku\.com/embed/\w{10,36}",
        "http[s]?://m\.youku\.com/video/id_\w{10,36}",
        "http[s]?://m\.youku\.com/alipay_video/id_\w{10,36}",
    ]

    TEST_CASE = [
        "https://v.youku.com/v_show/id_XNDI0MTQ4MzIwMA==.html?spm=a2ha1.12675304.m_5497_c_27681.d_1&scm=20140719.manual.5497.video_XNDI0MTQ4MzIwMA%3D%3D",
        "https://v.youku.com/v_show/id_XNDI0ODk0ODUzNg==.html?spm=a2ha1.12675304.m_2556_c_8261.d_1&s=de83005bc0ba4a9284b3&scm=20140719.manual.2556.show_de83005bc0ba4a9284b3",
        'http://player.youku.com/embed/XNDA3MjU1MzY3Ng==',
        'https://m.youku.com/video/id_XNDQ0MTY5MDc0OA==.html?%3Fspm=a2hww.12518357.yknav.14&spm=a2hww.12630586.entDrawer0.i0',
        'https://m.youku.com/alipay_video/id_XNDQ0MTg2MDk1Ng==.html?spm=a2hww.12630586.entDrawer2.1',
        "https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0",

        "https://v.youku.com/v_show/id_XNDIyMTIwMjc2MA==.html?spm=a2ha1.12675304.m_2556_c_8261.d_2&s=5b4e34d331864a6d89dc&scm=20140719.manual.2556.show_5b4e34d331864a6d89dc",
        "https://v.youku.com/v_show/id_XNDEyNDE5MzYyOA==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5MzYyOA%3D%3D",
        "https://v.youku.com/v_show/id_XMzIzNTkyNzYyOA==.html?spm=a2ha1.12675304.m_2561_c_8264.d_1&s=efbfbd043420efbfbdef&scm=20140719.rcmd.2561.show_efbfbd043420efbfbdef",
        "https://v.youku.com/v_show/id_XMTcxNTA2OTEwNA==.html?spm=a2ha1.12528442.m_4424_c_11054_4.d_5&s=cb4582f4f72011e5a080&scm=20140719.rcmd.4424.show_cb4582f4f72011e5a080",
        "https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D",

    ]

    def __init__(self, *args, **kwargs):
        ToolSet.__init__(self, *args, **kwargs)
        self.from_ = "youku"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        try:
            vid = webpage_url.split('?')[0].split('/')[-1].replace('==', '').lstrip('id_').split('.')[0]
        except:
            traceback.print_exc()
            return False
        else:
            webpage_url = f"https://v.youku.com/v_show/id_{vid}"
            data = {"video_id": vid,
                    "client_id": "b598bfd8ec862716",
                    "callback": "f'youkuPlayer_call_{int(time.time() * 1000)}'",
                    "type": "pc",
                    "embsig": "",
                    "version": "1.0",
                    "_t": "006315043435963385"}
            yk_url = 'https://api.youku.com/players/custom.json?'
            html = await self.request(
                url=yk_url,
                session=session,
                params=data,
                ssl=False,
            )

            customdata = json.loads(html)
            stealsign = customdata['stealsign']
            gather_results = await asyncio.gather(*[
                self.extract_info(vid=vid, sign=stealsign, client_id=data['client_id'], session=session),
                self.extract_comment_count(vid=vid, session=session),
                self.extract_webpage(url=webpage_url, session=session)
            ])
            result = self.merge_dicts(
                {
                    # "webpage_url": webpage_url,
                    "vid": vid,
                    "downloader": "ytd",
                },
                *gather_results[:2]
            )
            return {**gather_results[2], **result}

    @RequestRetry(default_exception_return={},
                  default_other_exception_return={})
    async def extract_info(self, vid, sign, client_id, session):
        new_parm = {'vid': vid,
                    'ccode': '0512',
                    'client_ip': '192.168.1.1',
                    'utid': 'lwF+FVFsUk4CAXF3uLWWBhbj',
                    'client_ts': str(int(time.time())),
                    'r': sign,
                    'ckey': 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND',
                    'site': '1',
                    'wintype': 'BDskin',
                    'p': '1',
                    'fu': '0',
                    'vs': '1.0',
                    'rst': 'mp4',
                    'dq': 'mp4',
                    'os': 'win',
                    'osv': '',
                    'd': '0',
                    'bt': 'pc',
                    'aw': 'w',
                    'needbf': '1',
                    'atm': '',
                    'partnerid': client_id,
                    'callback': f'youkuPlayer_call_{str(int(time.time() * 1000))}',
                    '_t': '08079273092687054'
                    }
        headers = {'Host': 'ups.youku.com',
                   'Referer': f'https://player.youku.com/embed/XNDIxNTA1MjEwNA==?client_id={client_id}&password=&autoplay=false',
                   'User-Agent': self.random_ua(),
                   }
        api = 'https://ups.youku.com/ups/get.json?'
        html = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=new_parm,
            ssl=False
        )
        videodata = json.loads(html.replace(new_parm['callback'], '')[1:-1])
        data = jmespath.search("data", videodata)
        try:
            height = jmespath.search('max_by(data.stream, &size).height', videodata)
            width = jmespath.search('max_by(data.stream, &size).width', videodata)
            # item['cdn_url'] = jmespath.search('max_by(data.stream, &size).segs[].cdn_url', videodata)
            play_addr = jmespath.search('max_by(data.stream, &size).segs[].cdn_url', videodata)[0]
        except:
            traceback.print_exc()
            height = jmespath.search('data.stream[-1].height', videodata)
            width = jmespath.search('data.stream[-1].width', videodata)
            # item['cdn_url'] = jmespath.search('data.stream[-1].segs[].cdn_url', videodata)
            play_addr = jmespath.search('data.stream[-1].segs[].cdn_url', videodata)[0]
        result = {
            # "from": self.from_,
            "duration": jmespath.search('video.seconds', data),
            "cover": jmespath.search('video.logo', data),
            "author": jmespath.search('uploader.username', data),
            "author_id": jmespath.search('uploader.uid', data),
            "author_url": jmespath.search('uploader.homepage', data),
            "author_avatar": jmespath.search('uploader.avatar.xlarge', data),
            "title": jmespath.search('video.title', data),
            "category": jmespath.search('video.subcategories[].name', data),
            "region": jmespath.search('video.network.country_code', data),
            "upload_ts": jmespath.search('video.ups.ups_ts', data),
            "height": height,
            "width": width,
            "play_addr": play_addr,
        }
        return result

    @RequestRetry(default_exception_return={},
                  default_other_exception_return={})
    async def extract_comment_count(self, vid, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['authority'] = 'p.comments.youku.com'
        params = (
            ('jsoncallback', 'n_commentList'),
            ('app', '100-DDwODVkv'),
            ('objectId', vid),
            ('listType', '0'),
            ('sign', '1bda07104b5c60f24b3ff236d46ee2c5'),
            ('time', '1558691658'),
        )
        api = 'https://p.comments.youku.com/ycp/comment/pc/commentList'
        response_text = await self.request(
            url=api,
            session=session,
            headers=headers,
            params=params,
            ssl=False
        )
        response_json = json.loads(response_text[len('  n_commentList('):-1])
        return {'comment_count': jmespath.search('data.totalSize', response_json)}

    async def extract_webpage(self, url, session):

        headers = self.general_headers(user_agent=self.random_ua())
        headers['authority'] = 'v.youku.com'
        headers['referer'] = 'https://www.youku.com/'

        text = await self.request(
            url=url,
            session=session,
            headers=headers,
            ssl=False
        )
        try:
            selector = Selector(text=text)
        except Exception:
            traceback.print_exc()
            return {}
        else:
            category = selector.css('head meta[name*="irCate"]::attr(content)').extract_first()
            category = category.split(',') if category else []
            rating = selector.css('.score').re('<em>(\d)</em>.(\d)</span>')
            tag = selector.css('head meta[name*="keywords"]::attr(content)').extract_first()
            tag = tag.split(',') if tag else None
            description = selector.css('head meta[name*="description"]::attr(content)').extract_first()
            if rating:
                try:
                    rating = float('.'.join(rating))
                except Exception:
                    traceback.format_exc()
                    return {'category': category, "tag": tag, "description": description}
                else:
                    return {'category': category, 'rating': rating, "tag": tag, "description": description}
            else:
                return {'category': category, "tag": tag, "description": description}


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

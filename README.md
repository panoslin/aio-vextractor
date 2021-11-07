# aioVextractor

Extract video structured data from more than 40 websites/mobile apps/H5 pages. Supporting TikTok, Youtube, Instagram, etc.

解析视频 网站/APP/H5 页面视频信息。支持抖音、腾讯视频、YouTube、Instagram 等40余个网站与APP


##### 开发文档

1. docker便捷部署
    ```bash
    git clone https://github.com/panoslin/aioVextractor &&\
    cd aioVextractor &&\
    sudo chmod +x build.sh &&\
    sudo sh build.sh
    ```

3. 使用
    ```python
    from aioVextractor.api import (
        extract,
        breakdown,
        hybrid_worker
    )
    import aiohttp
    import asyncio
    
    async def test():
        async with aiohttp.ClientSession() as session:
            single_url = "https://creative.adquan.com/show/286788"
            playlist_url = "https://weibo.com/p/1005055882998192/photos?type=video#place"
            print(await extract(webpage_url=single_url, session=session))
            print(await hybrid_worker(webpage_url=single_url, session=session))
            print(await breakdown(webpage_url=playlist_url, session=session))
            print(await hybrid_worker(webpage_url=playlist_url, session=session))
    
    
    asyncio.run(test())
    ```
    以上提供最高级的 API 解析视频网页链接
    * `extract`: 解析单个视频网址
    * `breakdown`: 解析整个播放列表网址
    * `hybrid_worker`: 自动检测网页是否为 单个视频网址/播放列表网址 并且返回对应结果
    
4. 支持的网站
    * youtube
    * tvcf
    * vimeo
    * vmovier
    * iwebad
    * douyin
    * naver
    * hellorf
    * pinterest
    * digitaling
    * weibo
    * adquan
    * xinpianchang
    * carben
    * bilibili
    * tencent
    * instagram
    * lanfan
    * youku
    * renren
    * socialbeta
    * weixin
    * eyepetizer

5. 测试Demo
    ```python
    from aioVextractor.extractor.tencent import Extractor as tencentIE
    from pprint import pprint
    
    with tencentIE() as extractor:
        webpage_url = "https://v.qq.com/iframe/player.html?vid=c0912n1rqrw&tiny=0&auto=0"
        res = extractor.sync_entrance(webpage_url=webpage_url)
        pprint(res)
    
    """
    OUTPUT:
    [{'ad_link': None,
      'author': 'Apple 官方频道',
      'author_attention': None,
      'author_avatar': None,
      'author_birthday': None,
      'author_description': None,
      'author_follwer_count': None,
      'author_follwing_count': None,
      'author_gender': None,
      'author_id': None,
      'author_sign': None,
      'author_url': 'http://v.qq.com/vplus/c855f20d041bc7e06f356522325b0902',
      'author_videoNum': None,
      'category': None,
      'cdn_url': None,
      'collect_count': None,
      'comment_count': None,
      'cover': 'http://vpic.video.qq.com/0/c0912n1rqrw.png',
      'description': None,
      'dislike_count': None,
      'download_count': None,
      'downloader': 'aria2c',
      'duration': '30',
      'forward_count': None,
      'from': 'tencent',
      'gender': None,
      'height': None,
      'language': None,
      'like_count': None,
      'play_addr': 'http://video.dispatch.tc.qq.com/uwMROfz2r5zIIaQXGdGlQmdfDmZvd0vRcymWSecrfGm8rzTb/c0912n1rqrw.mp4?vkey=0A9434327F854F742C34AEA63A4F5D91ECD3BD9941D4A21621691B03C74371E884E6AF55D20955207FFCE82AA75A01A55B29C753410E57BDCD9CB487C427D06C88D3DC8EEAF862862C5ACE1D009EA9AB4E9E9FD248C76EA2072BCAF06BA0F96DE76EE242119D5AAC873A6C18214552B745D194B35B1F1525CBE32AC7B90C7EAA',
      'rating': None,
      'recommend': None,
      'region': None,
      'share_count': None,
      'tag': ['敬 Mac 背后的你 - 试出可能 - Apple',
              '腾讯视频',
              '电影',
              '电视剧',
              '综艺',
              '新闻',
              '财经',
              '音乐',
              'MV',
              '高清',
              '视频',
              '在线观看'],
      'title': '敬 Mac 背后的你 - 试出可能 - Apple',
      'upload_date': None,
      'upload_ts': 1262275200,
      'vid': 'c0912n1rqrw',
      'view_count': '246304',
      'webpage_url': 'https://v.qq.com/x/page/c0912n1rqrw.html',
      'width': None}]
    """
    ```

6. 测试Demo
    ```python
    from aioVextractor.api import hybrid_worker
    import aiohttp
    import asyncio
    from pprint import pprint
    
    async def test(url):
        async with  aiohttp.ClientSession() as session:
            result = await hybrid_worker(
                webpage_url=url,
                session=session,
            )
            return result
    
    url = "https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc"  ## u can try any url from `TEST_CASE`
    pprint(asyncio.run(test(url=url)))
    
    
    """
    OUTPUT:
    Processing URL: https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc
    ([{'ad_link': None,
       'author': None,
       'author_attention': None,
       'author_avatar': None,
       'author_birthday': None,
       'author_description': None,
       'author_follwer_count': None,
       'author_follwing_count': None,
       'author_gender': None,
       'author_id': None,
       'author_sign': None,
       'author_url': None,
       'author_videoNum': None,
       'category': None,
       'cdn_url': None,
       'collect_count': None,
       'comment_count': None,
       'cover': 'https://i.ytimg.com/vi/61CQm2zVVk0/hqdefault.jpg?sqp=-oaymwEZCPYBEIoBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLAKICJl2FlmleQsKntUd0KIeOEjZA',
       'description': None,
       'dislike_count': None,
       'download_count': None,
       'downloader': 'ytd',
       'duration': None,
       'forward_count': None,
       'from': 'youtube',
       'gender': None,
       'height': None,
       'language': None,
       'like_count': None,
       'play_addr': None,
       'playlist_url': 'https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc',
       'rating': None,
       'recommend': None,
       'region': None,
       'share_count': None,
       'tag': None,
       'title': "The Avengers Earth's Mightiest Heroes Se1 - Ep01 Breakout (Part "
                '1) - Part 01',
       'upload_date': None,
       'upload_ts': None,
       'vid': '61CQm2zVVk0',
       'view_count': None,
       'webpage_url': 'https://www.youtube.com/watch?v=61CQm2zVVk0&list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc&index=2&t=0s',
       'width': None},
       ...
      {'ad_link': None,
       'author': None,
       'author_attention': None,
       'author_avatar': None,
       'author_birthday': None,
       'author_description': None,
       'author_follwer_count': None,
       'author_follwing_count': None,
       'author_gender': None,
       'author_id': None,
       'author_sign': None,
       'author_url': None,
       'author_videoNum': None,
       'category': None,
       'cdn_url': None,
       'collect_count': None,
       'comment_count': None,
       'cover': 'https://i.ytimg.com/vi/PRT3FjaP71E/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLA2zBcMa68iPw6tQO5nSbKlkwFv8w',
       'description': None,
       'dislike_count': None,
       'download_count': None,
       'downloader': 'ytd',
       'duration': None,
       'forward_count': None,
       'from': 'youtube',
       'gender': None,
       'height': None,
       'language': None,
       'like_count': None,
       'play_addr': None,
       'playlist_url': 'https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc',
       'rating': None,
       'recommend': None,
       'region': None,
       'share_count': None,
       'tag': None,
       'title': "The Avengers Earth's Mightiest Heroes Se1 - Ep10 Everything Is "
                'Wonderful - Screen 04',
       'upload_date': None,
       'upload_ts': None,
       'vid': 'PRT3FjaP71E',
       'view_count': None,
       'webpage_url': 'https://www.youtube.com/watch?v=PRT3FjaP71E&list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc&index=101&t=0s',
       'width': None}],
     True,
     {'clickTrackingParams': 'CD0QybcCIhMI16ucw-G35QIV40L1BR0A1weh',
      'continuation': '4qmFsgI2EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDmVnWlFWRHBEUjFFJTNE'})
    """
    ```

7. 测试通过链接：
    * [https://creative.adquan.com/show/286788](https://creative.adquan.com/show/286788)
    * [https://creative.adquan.com/show/286778](https://creative.adquan.com/show/286778)
    * [http://www.adquan.com/post-2-49507.html](http://www.adquan.com/post-2-49507.html)
    * [http://creative.adquan.com/show/49469](http://creative.adquan.com/show/49469)
    * [http://creative.adquan.com/show/49415](http://creative.adquan.com/show/49415)
    * [https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4](https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4)
    * [https://carben.me/video/9049](https://carben.me/video/9049)
    * [https://www.digitaling.com/projects/55684.html](https://www.digitaling.com/projects/55684.html)
    * [https://www.digitaling.com/projects/56636.html](https://www.digitaling.com/projects/56636.html)
    * [https://www.digitaling.com/articles/105167.html](https://www.digitaling.com/articles/105167.html)
    * [http://v.douyin.com/hd9sb3/](http://v.douyin.com/hd9sb3/)
    * [www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25](www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25)
    * [https://www.hellorf.com/video/show/15148543](https://www.hellorf.com/video/show/15148543)
    * [https://www.hellorf.com/video/show/11995691](https://www.hellorf.com/video/show/11995691)
    * [https://www.instagram.com/p/B1tXMlihthT/](https://www.instagram.com/p/B1tXMlihthT/)
    * [http://iwebad.com/video/3578.html](http://iwebad.com/video/3578.html)
    * [http://iwebad.com/video/3577.html](http://iwebad.com/video/3577.html)
    * [https://lanfanapp.com/recipe/3127/](https://lanfanapp.com/recipe/3127/)
    * [http://blog.naver.com/PostList.nhn?blogId=paranzui&categoryNo=0&from=postList](http://blog.naver.com/PostList.nhn?blogId=paranzui&categoryNo=0&from=postList)
    * [http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221233413302&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11](http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221233413302&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11)
    * [http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221239676910&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11](http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221239676910&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11)
    * [http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221227458497&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=29&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=29](http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221227458497&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=29&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=29)
    * [https://www.pinterest.com/pin/457256168416688731](https://www.pinterest.com/pin/457256168416688731)
    * [https://mobile.rr.tv/mission/#/share/video?id=1879897](https://mobile.rr.tv/mission/#/share/video?id=1879897)
    * [https://mobile.rr.tv/mission/#/share/video?id=1879530](https://mobile.rr.tv/mission/#/share/video?id=1879530)
    * [https://socialbeta.com/t/jiafangyifang-news-20190226](https://socialbeta.com/t/jiafangyifang-news-20190226)
    * [https://socialbeta.com/t/case-collection-overseas-ad-about-superbowl-20190224](https://socialbeta.com/t/case-collection-overseas-ad-about-superbowl-20190224)
    * [https://v.qq.com/x/page/s0886ag14xn.html](https://v.qq.com/x/page/s0886ag14xn.html)
    * [https://v.qq.com/x/page/n0864edqzkl.html](https://v.qq.com/x/page/n0864edqzkl.html)
    * [https://v.qq.com/x/page/s08899ss07p.html](https://v.qq.com/x/page/s08899ss07p.html)
    * [https://v.qq.com/x/cover/bzfkv5se8qaqel2.html](https://v.qq.com/x/cover/bzfkv5se8qaqel2.html)
    * [https://v.qq.com/iframe/player.html?vid=c0912n1rqrw&tiny=0&auto=0](https://v.qq.com/iframe/player.html?vid=c0912n1rqrw&tiny=0&auto=0)
    * [https://v.qq.com/iframe/preview.html?width=500&height=375&auto=0&vid=m0927lumf50](https://v.qq.com/iframe/preview.html?width=500&height=375&auto=0&vid=m0927lumf50)
    * [http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280](http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280)
    * [https://play.tvcf.co.kr/750556](https://play.tvcf.co.kr/750556)
    * [https://play.tvcf.co.kr/755843](https://play.tvcf.co.kr/755843)
    * [https://vimeo.com/281493330](https://vimeo.com/281493330)
    * [https://vimeo.com/344361560](https://vimeo.com/344361560)
    * [https://www.vmovier.com/55810?from=index_new_img](https://www.vmovier.com/55810?from=index_new_img)
    * [https://www.vmovier.com/56000?from=index_new_img](https://www.vmovier.com/56000?from=index_new_img)
    * [https://www.vmovier.com/56052?from=index_new_title](https://www.vmovier.com/56052?from=index_new_title)
    * [https://www.vmovier.com/55952?from=index_new_img](https://www.vmovier.com/55952?from=index_new_img)
    * [https://www.vmovier.com/55108](https://www.vmovier.com/55108)
    * [https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw](https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw)
    * [https://weibo.com/tv/v/I5RTQlExh?fid=1034:4413979699688929](https://weibo.com/tv/v/I5RTQlExh?fid=1034:4413979699688929)
    * [https://weibo.com/tv/v/FxTBC1Dp8?from=vhot](https://weibo.com/tv/v/FxTBC1Dp8?from=vhot)
    * [https://weibo.com/tv/v/Ib31ooLdE?fid=1034:4426329710596386](https://weibo.com/tv/v/Ib31ooLdE?fid=1034:4426329710596386)
    * [https://weibo.com/tv/v/IbOnau1mu?fid=1034:4428150730652786](https://weibo.com/tv/v/IbOnau1mu?fid=1034:4428150730652786)
    * [https://weibo.com/tv/v/IbFq32OZd?fid=1034:4427803702006591](https://weibo.com/tv/v/IbFq32OZd?fid=1034:4427803702006591)
    * [https://weibo.com/tv/v/I4YSOoeCp?fid=1034:4411872741380331](https://weibo.com/tv/v/I4YSOoeCp?fid=1034:4411872741380331)
    * [https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding](https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding)
    * [http://t.cn/Ai8Bj0z6](http://t.cn/Ai8Bj0z6)
    * [https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding](https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding)
    * [https://www.xinpianchang.com/a10475334?from=ArticleList](https://www.xinpianchang.com/a10475334?from=ArticleList)
    * [https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0](https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0)
    * [https://v.youku.com/v_show/id_XNDIyMTIwMjc2MA==.html?spm=a2ha1.12675304.m_2556_c_8261.d_2&s=5b4e34d331864a6d89dc&scm=20140719.manual.2556.show_5b4e34d331864a6d89dc](https://v.youku.com/v_show/id_XNDIyMTIwMjc2MA==.html?spm=a2ha1.12675304.m_2556_c_8261.d_2&s=5b4e34d331864a6d89dc&scm=20140719.manual.2556.show_5b4e34d331864a6d89dc)
    * [https://v.youku.com/v_show/id_XNDEyNDE5MzYyOA==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5MzYyOA%3D%3D](https://v.youku.com/v_show/id_XNDEyNDE5MzYyOA==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5MzYyOA%3D%3D)
    * [https://v.youku.com/v_show/id_XMzIzNTkyNzYyOA==.html?spm=a2ha1.12675304.m_2561_c_8264.d_1&s=efbfbd043420efbfbdef&scm=20140719.rcmd.2561.show_efbfbd043420efbfbdef](https://v.youku.com/v_show/id_XMzIzNTkyNzYyOA==.html?spm=a2ha1.12675304.m_2561_c_8264.d_1&s=efbfbd043420efbfbdef&scm=20140719.rcmd.2561.show_efbfbd043420efbfbdef)
    * [https://v.youku.com/v_show/id_XNDI0MTQ4MzIwMA==.html?spm=a2ha1.12675304.m_5497_c_27681.d_1&scm=20140719.manual.5497.video_XNDI0MTQ4MzIwMA%3D%3D](https://v.youku.com/v_show/id_XNDI0MTQ4MzIwMA==.html?spm=a2ha1.12675304.m_5497_c_27681.d_1&scm=20140719.manual.5497.video_XNDI0MTQ4MzIwMA%3D%3D)
    * [https://v.youku.com/v_show/id_XMTcxNTA2OTEwNA==.html?spm=a2ha1.12528442.m_4424_c_11054_4.d_5&s=cb4582f4f72011e5a080&scm=20140719.rcmd.4424.show_cb4582f4f72011e5a080](https://v.youku.com/v_show/id_XMTcxNTA2OTEwNA==.html?spm=a2ha1.12528442.m_4424_c_11054_4.d_5&s=cb4582f4f72011e5a080&scm=20140719.rcmd.4424.show_cb4582f4f72011e5a080)
    * [https://v.youku.com/v_show/id_XNDI0ODk0ODUzNg==.html?spm=a2ha1.12675304.m_2556_c_8261.d_1&s=de83005bc0ba4a9284b3&scm=20140719.manual.2556.show_de83005bc0ba4a9284b3](https://v.youku.com/v_show/id_XNDI0ODk0ODUzNg==.html?spm=a2ha1.12675304.m_2556_c_8261.d_1&s=de83005bc0ba4a9284b3&scm=20140719.manual.2556.show_de83005bc0ba4a9284b3)
    * [https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D](https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D)
    * [http://player.youku.com/embed/XNDA3MjU1MzY3Ng==](http://player.youku.com/embed/XNDA3MjU1MzY3Ng==)
    * [https://www.youtube.com/watch?v=tofSaLB9kwE](https://www.youtube.com/watch?v=tofSaLB9kwE)
    * [https://www.youtube.com/watch?v=pgN-vvVVxMA](https://www.youtube.com/watch?v=pgN-vvVVxMA)
    * [https://www.youtube.com/watch?v=iAeYPfrXwk4](https://www.youtube.com/watch?v=iAeYPfrXwk4)
    * [https://www.youtube.com/watch?v=jDO2YPGv9fw&list=PLNHZSfaJJc25zChky2JaM99ba8I2bVUza&index=15&t=0s](https://www.youtube.com/watch?v=jDO2YPGv9fw&list=PLNHZSfaJJc25zChky2JaM99ba8I2bVUza&index=15&t=0s)
    * [https://www.youtube.com/watch?v=JGwWNGJdvx8&list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs&index=28&t=0s](https://www.youtube.com/watch?v=JGwWNGJdvx8&list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs&index=28&t=0s)
    * [https://space.bilibili.com/29296192/video](https://space.bilibili.com/29296192/video)
    * [https://www.instagram.com/funnymike/](https://www.instagram.com/funnymike/)
    * [https://www.instagram.com/filmmkrs?igshid=186z6y04dov3y](https://www.instagram.com/filmmkrs?igshid=186z6y04dov3y)
    * [https://www.pinterest.com/luvbridal/video_pins/](https://www.pinterest.com/luvbridal/video_pins/)
    * [https://vimeo.com/alitasmitmedia](https://vimeo.com/alitasmitmedia)
    * [https://weibo.com/p/1005055882998192/photos?type=video#place](https://weibo.com/p/1005055882998192/photos?type=video#place)
    * [https://weibo.com/kongxiaorui?refer_flag=1005055014_](https://weibo.com/kongxiaorui?refer_flag=1005055014_)
    * [https://weibo.com/u/1927564525](https://weibo.com/u/1927564525)
    * [https://www.xinpianchang.com/u10014261?from=userList](https://www.xinpianchang.com/u10014261?from=userList)
    * [https://www.xinpianchang.com/u10029931?from=userList](https://www.xinpianchang.com/u10029931?from=userList)
    * [https://www.xinpianchang.com/u10002513?from=userList](https://www.xinpianchang.com/u10002513?from=userList)
    * [https://www.youtube.com/channel/UCSRpCBq2xomj7Sz0od73jWw/videos](https://www.youtube.com/channel/UCSRpCBq2xomj7Sz0od73jWw/videos)
    * [https://www.youtube.com/channel/UCAyj5vEhoaw6fDFBpSbQvRg](https://www.youtube.com/channel/UCAyj5vEhoaw6fDFBpSbQvRg)
    * [https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc](https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc)

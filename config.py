#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

# import time
import os

## retry at most 3 times when encounters failure request
RETRY = 3

URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

## indicator to show the significance level of the fields
FIELD_SIGNI_LEVEL = {
    "must": 1,  ## necessary field that should be present after extracting
    "else": 0,  ## not necessary
    "condition_must": 2  ## conditional necessary such as `play_addr` shold be present while `downloader` is aria2c
}

## desired output fields
## a mapping between field names and FIELD_SIGNI_LEVEL
## signi_level: one of the value in FIELD_SIGNI_LEVEL's values
## default_value: the default value if the results of Extractor.entrance() does not return
## dependent_field_name: if signi_level == 2, this should be the dependent field name.
## i.e. `downloader` for `play_addr`
## dependent_field_value: if signi_level == 2, this should be the dependent field value.
## i.e. `aria2c` for `play_addr`
## or True: meaning that this field should be provided as long as dependent_field_name is not None
FIELDS = {
    'ad_link': {"signi_level": 0, "default_value": None}, ## 视频对应广告链接
    'author': {"signi_level": 0, "default_value": None},  ## 作者名称
    'author_avatar': {"signi_level": 0, "default_value": None},  ## 作者头像
    'author_birthday': {"signi_level": 0, "default_value": None},  ## 作者生日
    'author_description': {"signi_level": 0, "default_value": None},  ## 作者简介
    'author_follwer_count': {"signi_level": 0, "default_value": None},  ## 作者粉丝数
    'author_follwing_count': {"signi_level": 0, "default_value": None},  ## 作者关注用户数
    'author_id': {"signi_level": 0, "default_value": None},  ## 作者 ID
    'author_sign': {"signi_level": 0, "default_value": None},  ## 作者签名
    'author_url': {"signi_level": 0, "default_value": None},  ## 作者页面 URL
    'author_videoNum': {"signi_level": 0, "default_value": None},  ## 作者视频数量
    'category': {"signi_level": 0, "default_value": None},  ## 视频分类
    # 'cdn_url': {"signi_level": 0, "default_value": None},
    'collect_count': {"signi_level": 0, "default_value": None},  ## 视频被收藏次数
    'comment_count': {"signi_level": 0, "default_value": None},  ## 视频评论数
    'cover': {"signi_level": 1},  ## 视频封面 URL
    # 'created_at': {"signi_level": 0, "default_value": int(time.time())},
    'description': {"signi_level": 0, "default_value": None},  ## 视频简介
    'dislike_count': {"signi_level": 0, "default_value": None},  ## 视频 "踩" 数量
    'download_count': {"signi_level": 0, "default_value": None},  ## 视频下载次数
    'downloader': {"signi_level": 0, "default_value": "aria2c"},  ## 视频使用的下载器，默认 Aria2c
    'duration': {"signi_level": 0, "default_value": None},  ## 视频时长
    'forward_count': {"signi_level": 0, "default_value": None},  ## 视频转发数
    'from': {"signi_level": 1},  ## 视频来源网站代号
    'gender': {"signi_level": 0, "default_value": None},  ## 作者性别
    'height': {"signi_level": 0, "default_value": None},  ## 视频高度
    'language': {"signi_level": 0, "default_value": None},  ## 视频语言
    'like_count': {"signi_level": 0, "default_value": None},  ## 视频点赞数
    'play_addr': {"signi_level": 2, "default_value": None,
                  "dependent_field_name": "downloader",
                  "dependent_field_value": "aria2c"},  ## 视频播放 URL
    # 'player_id',
    'rating': {"signi_level": 0, "default_value": None},  ## 视频评分
    'recommend': {"signi_level": 0, "default_value": None},  ## 视频推荐（是否推荐 或者 推荐的分类）
    'region': {"signi_level": 0, "default_value": None},  ## 视频地区
    'share_count': {"signi_level": 0, "default_value": None},  ## 视频分享次数
    'tag': {"signi_level": 0, "default_value": None},  ## 视频标签
    'title': {"signi_level": 0, "default_value": None},  ## 视频标题
    # 'upload_date': {"signi_level": 0, "default_value": None},  ## 视频上传日期
    'upload_ts': {"signi_level": 0, "default_value": None},  ## 视频上传时间戳
    'vid': {"signi_level": 1},  ## 视频原网站 ID
    'view_count': {"signi_level": 0, "default_value": None},  ## 视频播放次数
    'webpage_url': {"signi_level": 1},  ## 视频源网页 URL
    'width': {"signi_level": 0, "default_value": None}, ## 视频宽度
}

FIELDS_BREAKDOWN = {
    'playlist_url': {"signi_level": 1},

    'ad_link': {"signi_level": 0, "default_value": None},
    'author': {"signi_level": 0, "default_value": None},
    'author_attention': {"signi_level": 0, "default_value": None},
    'author_avatar': {"signi_level": 0, "default_value": None},
    'author_birthday': {"signi_level": 0, "default_value": None},
    'author_description': {"signi_level": 0, "default_value": None},
    'author_follwer_count': {"signi_level": 0, "default_value": None},
    'author_follwing_count': {"signi_level": 0, "default_value": None},
    'author_gender': {"signi_level": 0, "default_value": None},
    'author_id': {"signi_level": 0, "default_value": None},
    'author_sign': {"signi_level": 0, "default_value": None},
    'author_url': {"signi_level": 0, "default_value": None},
    'author_videoNum': {"signi_level": 0, "default_value": None},
    'category': {"signi_level": 0, "default_value": None},
    'cdn_url': {"signi_level": 0, "default_value": None},
    'collect_count': {"signi_level": 0, "default_value": None},
    'comment_count': {"signi_level": 0, "default_value": None},
    'cover': {"signi_level": 1},
    # 'created_at': {"signi_level": 0, "default_value": int(time.time())},
    'description': {"signi_level": 0, "default_value": None},
    'dislike_count': {"signi_level": 0, "default_value": None},
    'download_count': {"signi_level": 0, "default_value": None},
    'downloader': {"signi_level": 0, "default_value": "aria2c"},
    'duration': {"signi_level": 0, "default_value": None},
    'forward_count': {"signi_level": 0, "default_value": None},
    'from': {"signi_level": 1},
    'gender': {"signi_level": 0, "default_value": None},
    'height': {"signi_level": 0, "default_value": None},
    'language': {"signi_level": 0, "default_value": None},
    'like_count': {"signi_level": 0, "default_value": None},
    'play_addr': {"signi_level": 0, "default_value": None},
    # 'player_id',
    'rating': {"signi_level": 0, "default_value": None},
    'recommend': {"signi_level": 0, "default_value": None},
    'region': {"signi_level": 0, "default_value": None},
    'share_count': {"signi_level": 0, "default_value": None},
    'tag': {"signi_level": 0, "default_value": None},
    'title': {"signi_level": 0, "default_value": None},
    'upload_date': {"signi_level": 0, "default_value": None},
    'upload_ts': {"signi_level": 0, "default_value": None},
    'vid': {"signi_level": 1},
    'view_count': {"signi_level": 0, "default_value": None},
    'webpage_url': {"signi_level": 1},
    'width': {"signi_level": 0, "default_value": None},

}

FIELDS_RSS = {
    'player': {"signi_level": 0, "default_value": None},
    'player_id': {"signi_level": 2, "default_value": None,
                  "dependent_field_name": "player",
                  "dependent_field_value": True},  ## True meaning that this field should be provided as long as dependent_field_name is not None
    'multiplier': {"signi_level": 0, "default_value": 0},

    'ad_link': {"signi_level": 0, "default_value": None},
    'author': {"signi_level": 0, "default_value": None},
    'author_attention': {"signi_level": 0, "default_value": None},
    'author_avatar': {"signi_level": 0, "default_value": None},
    'author_birthday': {"signi_level": 0, "default_value": None},
    'author_description': {"signi_level": 0, "default_value": None},
    'author_follwer_count': {"signi_level": 0, "default_value": None},
    'author_follwing_count': {"signi_level": 0, "default_value": None},
    'author_gender': {"signi_level": 0, "default_value": None},
    'author_id': {"signi_level": 0, "default_value": None},
    'author_sign': {"signi_level": 0, "default_value": None},
    'author_url': {"signi_level": 0, "default_value": None},
    'author_videoNum': {"signi_level": 0, "default_value": None},
    'category': {"signi_level": 0, "default_value": None},
    'cdn_url': {"signi_level": 0, "default_value": None},
    'collect_count': {"signi_level": 0, "default_value": None},
    'comment_count': {"signi_level": 0, "default_value": None},
    'cover': {"signi_level": 1},
    # 'created_at': {"signi_level": 0, "default_value": int(time.time())},
    'description': {"signi_level": 0, "default_value": None},
    'dislike_count': {"signi_level": 0, "default_value": None},
    'download_count': {"signi_level": 0, "default_value": None},
    'downloader': {"signi_level": 0, "default_value": "aria2c"},
    'duration': {"signi_level": 0, "default_value": None},
    'forward_count': {"signi_level": 0, "default_value": None},
    'from': {"signi_level": 1},
    'gender': {"signi_level": 0, "default_value": None},
    'height': {"signi_level": 0, "default_value": None},
    'language': {"signi_level": 0, "default_value": None},
    'like_count': {"signi_level": 0, "default_value": None},
    'play_addr': {"signi_level": 0, "default_value": None},
    # 'player_id',
    'rating': {"signi_level": 0, "default_value": None},
    'recommend': {"signi_level": 0, "default_value": None},
    'region': {"signi_level": 0, "default_value": None},
    'share_count': {"signi_level": 0, "default_value": None},
    'tag': {"signi_level": 0, "default_value": None},
    'title': {"signi_level": 0, "default_value": None},
    'upload_date': {"signi_level": 0, "default_value": None},
    'upload_ts': {"signi_level": 0, "default_value": None},
    'vid': {"signi_level": 1},
    'view_count': {"signi_level": 0, "default_value": None},
    'webpage_url': {"signi_level": 1},
    'width': {"signi_level": 0, "default_value": None},

}

SANIC_PORT = 5555
SANIC_WORKER = min([os.cpu_count(), 5])
LOCAL_IP_ADDR = '0.0.0.0'
MAX_ESTIMATE_RECORD_NUMBER = 5000000
check_latest_buffer = 5  ## check_latest_buffer

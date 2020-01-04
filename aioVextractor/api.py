#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/25/19
# IDE: PyCharm


import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from aioVextractor import (
    distribute_webpage,
    distribute_playlist,
    distribute_hybrid
)


async def extract(webpage_url, session):
    """
    extract single webpage_url
    webpage_url can be single url join() by string than can separate any consecutive urls
    """
    print(f"Extracting URL: {webpage_url}")
    distribute_result = distribute_webpage(webpage_url=webpage_url)
    if isinstance(distribute_result, str):
        return distribute_result
    else:
        info_extractor = distribute_result
        with info_extractor() as dinosaur:
            result = await dinosaur.entrance(webpage_url=webpage_url, session=session)
            return result


async def breakdown(webpage_url, session, *args, **kwargs):
    print(f"Breaking URL: {webpage_url}")
    distribute_result = distribute_playlist(webpage_url=webpage_url)
    if isinstance(distribute_result, str):
        return distribute_result
    else:
        bk = distribute_result
        with bk() as dinosaur:
            result = await dinosaur.breakdown(webpage_url=webpage_url, session=session, *args, **kwargs)
            return result


async def hybrid_worker(webpage_url, session, *args, **kwargs):
    print(f"Processing URL: {webpage_url}")
    distribute_result = distribute_hybrid(webpage_url=webpage_url)
    if isinstance(distribute_result, str):
        return distribute_result
    else:
        instance = distribute_result
        if instance.__name__ == "Breaker":
            with instance() as breaker:
                result = await breaker.breakdown(
                    webpage_url=webpage_url,
                    session=session,
                    *args,
                    **kwargs
                )
        else:
            with instance() as extractor:
                result = await extractor.entrance(
                    webpage_url=webpage_url,
                    session=session,
                    *args,
                    **kwargs
                )
        return result

def set_up_proxy(proxy):
    """
    Set up http proxy globally.
    Run this before you set up aiohttp.ClientSession(trust_env=True) if you would like to use proxy
    :param proxy: format like "http://ip_addr:port"
    """
    if proxy:
        os.environ['HTTP_PROXY'] = proxy

if __name__ == '__main__':
    import aiohttp
    import asyncio
    async def test():
        async with aiohttp.ClientSession() as session:
            single_url = "https://creative.adquan.com/show/286788"
            playlist_url = "https://weibo.com/p/1005055882998192/photos?type=video#place"
            # print(await extract(webpage_url=single_url, session=session))
            # print(await hybrid_worker(webpage_url=single_url, session=session))
            # print(await breakdown(webpage_url=playlist_url, session=session))
            print(await hybrid_worker(webpage_url="https://instagram.com/renopedia?igshid=dpu27sj4wxok", session=session))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())

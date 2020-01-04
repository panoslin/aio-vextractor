#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/4/19
# IDE: PyCharm


from abc import (
    ABCMeta,
    abstractmethod
)

from aioVextractor.extractor.tool_set import (
    RequestRetry,
    BasicToolSet,
    validate_,
)

import asyncio
import aiohttp
import platform
import wrapt
import re
from aioVextractor import config
import jmespath
from bloom_filter import BloomFilter


# class RssMeta(metaclass=ABCMeta):




@wrapt.decorator
async def validate(func, extractor_instace, args, kwargs):
    """
    1. ensure the accuracy of the input url: match the url by `target_website` in class variable
    2. ensure the integrated of the output data according to the config.FIELDS_BREAKDOWN
    3. if multiple urls match, ONLY breakdown the first match
    4. filter repeated result according by output field `vid`
    :return:
    """
    # downloader = extractor_instace.downloader

    results = await func(*args, **kwargs)

    outputs = []

    ## if the results is []/False/None/0
    ## return None
    if results:
        pass
    else:
        return None

    # try:
    #     results, has_more, params = results
    # except:
    #     return "The return should be a 3-elements tuple"

    vid_filter = set()
    ## validate the integrity of the output
    for result in results:
        ## filter by `vid`
        try:
            vid = result['vid']
            if vid in vid_filter:
                continue
            else:
                vid_filter.add(result['vid'])
        except:
            # print(f"You should have specify field `vid`")
            return f"You should have specify field `vid`"
        output = validate_(
            result=result,
            check_field=config.FIELDS_RSS,
        )
        if output:  ## after scanning all the listed field in config.FIELDS_BREAKDOWN
            # output['downloader'] = downloader
            outputs.append(output)
    else:
        return outputs


class BaseRss(BasicToolSet, metaclass=ABCMeta):

    # downloader = 'aria2c'

    def sync_fetch(self, *args, **kwargs):
        """
        A synchronous entrance to call self.fetch()
        """

        async def wrapper():
            async with aiohttp.ClientSession() as session:
                return await self.fetch(session=session, *args, **kwargs)

        python_version = float(".".join(platform.python_version_tuple()[0:2]))
        if python_version >= 3.7:
            return asyncio.run(wrapper())
        elif 3.5 <= python_version <= 3.6:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(wrapper())
            loop.close()
            return results
        else:
            return f"The Python Interpreter you are using is {python_version}.\n" \
                   f"You should consider switching it to some more modern one such as Python 3.7+ " \
                .format(python_version=python_version)

    @validate
    @abstractmethod
    async def fetch(self, *args, **kwargs):
        return []

    @validate
    async def filter(self, existed_vid_list=None):
        bloom = BloomFilter(max_elements=config.MAX_ESTIMATE_RECORD_NUMBER)  ## construct a bloom filter
        for ele in existed_vid_list:
            bloom.add(ele)  ## add origin_id into the filter
        latest_results = []  ## final result to output
        ## The one who is responsible for the paging for xinpianchang do not have any kids
        buffer = config.check_latest_buffer
        latest = await self.fetch()
        for ele in latest:
            if bloom.__contains__(ele['vid']):  ## determine whether if the ele is reocrded
                ## if the ele is recorded
                ## meaning that the upcoming ele are repeated
                ## so we just return the current latest_results

                ## but due to the unreasonable paging issue
                ## we need a buffer to make sure that we make it to the end
                if buffer == 0:
                    del bloom  ## release memory
                    return jmespath.search('[]', latest_results) if latest_results else []
                else:
                    buffer -= 1
                    continue
            else:
                bloom.add(ele['vid'])  ## add origin_id into the filter
                latest_results.append(ele)
        else:
            return jmespath.search('[]', latest_results) if latest_results else []

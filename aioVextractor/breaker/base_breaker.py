#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/23/19
# IDE: PyCharm

from aioVextractor.extractor.tool_set import (
    BasicToolSet,
    validate_,
)

import config
import wrapt
import aiohttp
import platform
import asyncio
import re
import traceback
from abc import (
    ABCMeta,
    abstractmethod
)


@wrapt.decorator
async def validate(func, extractor_instace, args, kwargs):
    """
    1. ensure the accuracy of the input url: match the url by `target_website` in class variable
    2. ensure the integrated of the output data according to the config.FIELDS_BREAKDOWN
    3. if multiple urls match, ONLY breakdown the first match
    4. filter repeated result according by output field `vid`
    :return:
    """
    ## list of regexs for matching exact webpage_url for extractor_instance
    target_website = extractor_instace.target_website
    downloader = extractor_instace.downloader
    webpage_url = kwargs['webpage_url']
    urls = []
    ## match url form webpage_url
    for regex in target_website:
        urls += re.findall(regex, webpage_url)

    if not urls:
        print("There has no suitable url match!")
        return None

    results = await func(*args, **{**kwargs, **{"webpage_url": urls[0]}})

    outputs = []

    ## if the results is []/False/None/0
    ## return None
    if results:
        pass
    else:
        return None

    try:
        results, has_more, params = results
    except:
        return "The return should be a 3-elements tuple"

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
            check_field=config.FIELDS_BREAKDOWN,
        )
        if output:  ## after scanning all the listed field in config.FIELDS_BREAKDOWN
            output['downloader'] = downloader
            outputs.append(output)
    else:
        return outputs, has_more, params


# class BreakerMeta(metaclass=ABCMeta):
#
#     @abstractmethod
#     def breakdown(self, *args, **kwargs):
#         pass


class BaseBreaker(BasicToolSet, metaclass=ABCMeta):
    downloader = 'aria2c'

    @validate
    @abstractmethod
    async def breakdown(self, *args, **kwargs):
        pass


    def sync_breakdown(self, webpage_url, *args, **kwargs):
        """
        A synchronous entrance to call self.breakdown()
        :param webpage_url:
        :return:
        """

        async def wrapper():
            async with aiohttp.ClientSession() as session:
                try:
                    return await self.breakdown(webpage_url=webpage_url, session=session, *args, **kwargs)
                except:
                    traceback.print_exc()

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

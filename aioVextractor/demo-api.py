#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/15/19
# IDE: PyCharm

## add current path to system path temporary
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from sanic import response as Response
from sanic import Sanic
from sanic_cors import CORS
import platform
import aiohttp
import config
from aioVextractor.api import hybrid_worker
import base64
import json

app = Sanic('Extractor')
app.config.KEEP_ALIVE = True
app.config.KEEP_ALIVE_TIMEOUT = 500
app.config.RESPONSE_TIMEOUT = 500
CORS(app, automatic_options=True)


@app.route('/')
async def homepage(request):
    response = {k: {"method": v[1][1],
                    "url": app.url_for(k,
                                       _external=True,
                                       _server=f"http://{config.LOCAL_IP_ADDR}:{config.SANIC_PORT}"),
                    "pattern": v[1][2].pattern,
                    "parameters": v[1][3],
                    } for k, v in app.router.routes_names.items()}
    return Response.json(response)


@app.route('/extractor', methods=['GET', 'POST'], name='extractor')
async def extractor(request):
    if request.method == 'GET':
        url = request.args.get('url')
        encoded_params = request.args.get('next', b'e30=')
    else:  ## request.method == 'POST'
        try:
            url = request.json.get('url')
            encoded_params = request.json.get('next', b'e30=')
        except:
            url = request.form.get('url')
            encoded_params = request.form.get('next', b'e30=')
    if url:
        ## decode the necessary params for next page
        print(f"Receive URL: {url}")
        params = json.loads(str(base64.b64decode(encoded_params), 'utf-8'))
        async with  aiohttp.ClientSession() as session:
            result = await hybrid_worker(
                webpage_url=url,
                session=session,
                **params
            )

            if isinstance(result, str):
                return Response.json({"msg": result,
                                      "data": None},
                                     status=400)
            elif isinstance(result, tuple):  ## playlist
                outputs, has_more, params = result
                ## encode the necessary params for next page
                encoded_params = base64.b64encode(json.dumps(params).encode('utf-8'))
                page = params.get("page", 1)
                return Response.json({
                    "msg": "success",
                    "data": outputs,
                    "count": len(outputs),
                    "is_playlist": True,
                    "next": app.url_for('extractor',
                                        _external=True,
                                        _server=f"http://{config.LOCAL_IP_ADDR}:{config.SANIC_PORT}",
                                        url=url,
                                        page=page + 1,
                                        next=encoded_params)
                    if has_more else None
                })
            else:  ## webpage
                return Response.json({
                    "msg": "success",
                    "data": result,
                    "count": len(result),
                    "is_playlist": False,
                    "next": None,
                })
    else:
        return Response.json({"msg": "There is not enough input🤯",
                              "data": None},
                             status=400)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=config.SANIC_PORT,
            workers=config.SANIC_WORKER,
            debug=True,
            access_log=True,
            # strict_slashes=False,
            )

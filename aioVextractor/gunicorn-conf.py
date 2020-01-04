#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/3/29
# IDE: PyCharm
"""
gunicorn -c gunicorn/gunicorn_conf.py  gluttony.tony:app
-D Daemonize the Gunicorn process. Detaches the server from the controlling terminal and enters the background.
"""

import os

bind = f'0.0.0.0:5555'
## Gunicorn should only need 4-12 worker processes
## to handle hundreds or thousands of requests per second.
workers = min(os.cpu_count(), 5)
## The number of worker threads for handling requests.
## A positive integer generally in the 2-4 x $(NUM_CORES) range.
## You’ll want to vary this a bit to find the best for your particular application’s work load.
threads = min(os.cpu_count(), 5)
## Daemonize the Gunicorn process.
## Detaches the server from the controlling terminal and enters the background.
# daemon = True
reload = False

worker_class = 'sanic.worker.GunicornWorker'
## The maximum number of requests a worker will process before restarting.
## Any value greater than zero will limit the number of requests a work will process before automatically restarting.
## This is a simple method to help limit the damage of memory leaks.
## If this is set to zero (the default) then the automatic worker restarts are disabled.
# max_requests = 2000

## Workers silent for more than this many seconds are killed and restarted.
timeout = 60 * 60 *24

## After receiving a restart signal,
# workers have this much time to finish serving requests.
graceful_timeout = 60 * 5

## A dictionary containing headers and values that the front-end proxy uses to indicate HTTPS requests.
## These tell Gunicorn to set wsgi.url_scheme to https, so your application can tell that the request is secure.
## The dictionary should map upper-case header names to exact string values.
## The value comparisons are case-sensitive,
## unlike the header names, so make sure they’re exactly what your front-end proxy sends when handling HTTPS requests.
## It is important that your front-end proxy configuration ensures that
## the headers defined here can not be passed directly from the client.
## example:
## {'X-FORWARDED-PROTOCOL': 'ssl',
## 'X-FORWARDED-PROTO': 'https',
## 'X-FORWARDED-SSL': 'on'}
# secure_scheme_headers

## Front-end’s IPs from which allowed to handle set secure headers. (comma separate).
## Set to * to disable checking of Front-end IPs
## (useful for setups where you don’t know in advance the IP address of Front-end, but you still trust the environment).
# forwarded_allow_ips

## Front-end’s IPs from which allowed accept proxy requests (comma separate).
## Set to * to disable checking of Front-end IPs (useful for setups where you don’t know in advance the IP address of Front-end, but you still trust the environment)
# proxy_allow_ips

## Called just before the master process is initialized.
# def on_starting(server):
#     pass
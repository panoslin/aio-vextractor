#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm


from aiohttp.client_exceptions import (ServerDisconnectedError,
                                       ServerConnectionError,
                                       ClientOSError,
                                       ClientConnectorCertificateError,
                                       ServerTimeoutError,
                                       ContentTypeError,
                                       ClientConnectorError,
                                       ClientPayloadError)
from mysql.connector.errors import (OperationalError,
                                    ProgrammingError,
                                    DatabaseError,
                                    InterfaceError)
import asyncio

http_exception = (ServerDisconnectedError,
                  ServerConnectionError,
                  asyncio.TimeoutError,
                  ClientConnectorError,
                  ClientPayloadError,
                  ServerTimeoutError,
                  # ContentTypeError,
                  ClientConnectorCertificateError,
                  ClientOSError)

mysql_exception = (OperationalError,
                   ProgrammingError,
                   DatabaseError,
                   InterfaceError)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/13/18
# IDE: PyCharm

import mysql.connector
import traceback
from aioVextractor.utils.exception import mysql_exception
import wrapt
import functools
import config


def MysqlRetry(
        host,
        port,
        user_name,
        password,
        database=None,
        wrapped=None,
        default_exception_return=False,
        default_other_exception_return=False,
        **kwargs
):
    """
    work as a decorator
    providing keywork arguments for the decorated function
    containg kwargs['conn'] and kwargs['cur'],
    which are the MySQLConnection object and cursor object from mysql-connector-python, respectively.

    """
    if wrapped is None:
        return functools.partial(MysqlRetry,
                                 host=host,
                                 port=port,
                                 user_name=user_name,
                                 password=password,
                                 database=database,
                                 default_exception_return=default_exception_return,
                                 default_other_exception_return=default_other_exception_return,
                                 **kwargs
                                 )
    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):
        for _ in range(config.RETRY):
            try:
                kwargs['conn'], kwargs['cur'] = connect(
                    host=host,
                    port=port,
                    user_name=user_name,
                    password=password,
                    database=database,
                    **kwargs
                )
                res = func(*args, **kwargs)
            except mysql_exception:
                traceback.print_exc()
                kwargs['conn'].rollback()
                kwargs['cur'].close()
                kwargs['conn'].close()
                continue
            except:
                traceback.print_exc()
                kwargs['conn'].rollback()
                kwargs['cur'].close()
                kwargs['conn'].close()
                return default_other_exception_return
            else:
                kwargs['conn'].commit()
                kwargs['cur'].close()
                kwargs['conn'].close()
                return res
        else:
            return default_exception_return
    return wrapper(wrapped)


def connect(host, port, user_name, password, database, dictionary=True, **kwargs):
    # Construct MySQL connect
    conn = mysql.connector.connect(
        user=user_name,
        password=password,
        host=host,
        port=port,
        database=database,
        **kwargs
    )
    cur = conn.cursor(dictionary=dictionary)
    return conn, cur


def close(conn, cur):
    cur.close()
    conn.close()


def commit(conn):
    conn.commit()


def rollback(conn):
    conn.rollback()

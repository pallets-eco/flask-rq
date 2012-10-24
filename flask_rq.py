# -*- coding: utf-8 -*-
"""
    flask_rq
    ~~~~~~~~

    RQ (Redis Queue) integration for Flask applications.

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.

"""

from flask import current_app
from redis import Redis
from rq import Queue


default_config = {
    'RQ_DEFAULT_HOST': 'localhost',
    'RQ_DEFAULT_PORT': 6379,
    'RQ_DEFAULT_PASSWORD': None,
    'RQ_DEFAULT_DB': 0
}


def config_value(name, key):
    key = 'RQ_%s_%s' % (name.upper(), key)
    return current_app.config.get(key, None)


def get_connection(name='default'):
    return Redis(host=config_value(name, 'HOST'),
        port=config_value(name, 'PORT'),
        password=config_value(name, 'PASSWORD'),
        db=config_value(name, 'DB'))


def get_queue(name='default', **kwargs):
    kwargs['connection'] = get_connection(name)
    return Queue(name, **kwargs)


def enqueue(*args, **kwargs):
    with get_connection(kwargs.pop('connection', None)):
        q = get_queue(kwargs.pop('name', None))
        return q.enqueue(*args, **kwargs)


def task(func_or_queue=None, connection=None):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            with get_connection(connection):
                q = get_queue(func_or_queue)
                return q.enqueue(fn, *args, **kwargs)
        return decorator

    if callable(func_or_queue):
        return wrapper(func_or_queue)

    return wrapper


class RQ(object):
    def __init__(self, app):
        self.init_app(app)

    def init_app(self, app):
        for key, value in default_config.items():
            app.config.setdefault(key, value)

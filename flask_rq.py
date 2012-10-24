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
from rq.decorators import job


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


def task(func_or_queue=None, *args, **kwargs):
    if callable(func_or_queue):
        func = func_or_queue
        queue = get_queue('default')
    else:
        func = None
        queue = get_queue(func_or_queue)

    decorator = job(queue, connection=queue.connection, *args, **kwargs)

    if func:
        return decorator(func)
    return decorator


class RQ(object):
    def __init__(self, app):
        self.init_app(app)

    def init_app(self, app):
        for key, value in default_config.items():
            app.config.setdefault(key, value)

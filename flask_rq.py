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
from rq import Queue, Connection


default_config = {
    'RQ_DEFAULT_HOST': 'localhost',
    'RQ_DEFAULT_PORT': 6379,
    'RQ_DEFAULT_PASSWORD': None,
    'RQ_DEFAULT_DB': 0
}


def get_app(reference_app=None):
    if reference_app is not None:
        return reference_app
    return current_app


def config_value(name, key):
    key = 'RQ_%s_%s' % (name.upper(), key)
    return get_app().config.get(key, None)


def get_connection(name=None):
    name = name or 'default'

    return Connection(Redis(host=config_value(name, 'HOST'),
                            port=config_value(name, 'PORT'),
                            password=config_value(name, 'PASSWORD'),
                            db=config_value(name, 'DB')))


def get_queue(name=None, **kwargs):
    return Queue(name or 'default', **kwargs)


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

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        for key, value in default_config.items():
            app.config.setdefault(key, value)

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['rq'] = self

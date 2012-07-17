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

    def get_app(self, reference_app=None):
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        return current_app

    def config_value(self, name, key):
        key = 'RQ_%s_%s' % (name.upper(), key)
        return self.get_app().config.get(key, None)

    def get_connection(self, name=None):
        name = name or 'default'

        return Connection(Redis(host=self.config_value(name, 'HOST'),
                                port=self.config_value(name, 'PORT'),
                                password=self.config_value(name, 'PASSWORD'),
                                db=self.config_value(name, 'DB')))

    def get_queue(self, name=None, **kwargs):
        return Queue(name or 'default', **kwargs)

    def enqueue(self, *args, **kwargs):
        with self.get_connection(kwargs.pop('connection', None)):
            q = self.get_queue(kwargs.pop('name', None))
            return q.enqueue(*args, **kwargs)

    def task(self, func_or_queue=None, connection=None):
        def wrapper(fn):
            def decorator(*args, **kwargs):
                with self.get_connection(connection):
                    q = self.get_queue(func_or_queue)
                    return q.enqueue(fn, *args, **kwargs)
            return decorator

        if callable(func_or_queue):
            return wrapper(func_or_queue)

        return wrapper

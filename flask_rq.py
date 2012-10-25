# -*- coding: utf-8 -*-
"""
    flask_rq
    ~~~~~~~~

    RQ (Redis Queue) integration for Flask applications.

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.

"""
import redis

from flask import current_app
from redis._compat import urlparse
from rq import Queue, Worker
from rq.decorators import job


default_config = {
    'RQ_DEFAULT_HOST': 'localhost',
    'RQ_DEFAULT_PORT': 6379,
    'RQ_DEFAULT_PASSWORD': None,
    'RQ_DEFAULT_DB': 0
}


def config_value(name, key):
    name = name.upper()
    config_key = 'RQ_%s_%s' % (name, key)
    if not config_key in current_app.config \
            and not 'RQ_%s_URL' % name in current_app.config:
        config_key = 'RQ_DEFAULT_%s' % key
    return current_app.config.get(config_key, None)


def get_connection(queue='default'):
    url = config_value(queue, 'URL')
    if url:
        return redis.from_url(url, db=config_value(queue, 'DB'))
    return redis.Redis(host=config_value(queue, 'HOST'),
        port=config_value(queue, 'PORT'),
        password=config_value(queue, 'PASSWORD'),
        db=config_value(queue, 'DB'))


def get_queue(name='default', **kwargs):
    kwargs['connection'] = get_connection(name)
    return Queue(name, **kwargs)


def get_server_url(name):
    url = config_value(name, 'URL')
    if url:
        url_kwargs = urlparse(url)
        return '%s://%s' % (url_kwargs.scheme, url_kwargs.netloc)
    else:
        host = config_value(name, 'HOST')
        password = config_value(name, 'HOST')
        netloc = host if not password else ':%s@%s' % (password, host)
        return 'redis://%s' % netloc


def get_worker(queues=['default']):
    servers = [get_server_url(name) for name in queues]
    if not servers.count(servers[0]) == len(servers):
        raise Exception('A worker only accept one connection')
    return Worker([get_queue(name) for name in queues],
        connection=get_connection(queues[0]))


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

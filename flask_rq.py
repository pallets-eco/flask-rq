# -*- coding: utf-8 -*-
"""
    flask_rq
    ~~~~~~~~

    RQ (Redis Queue) integration for Flask applications.

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.

"""
import collections

import redis
import rq

__version__ = '1.0'


class FlaskRQ(object):
    DEFAULT_QUEUE_NAME = 'default'

    _app = None
    queues = collections.OrderedDict()

    redis_connection = None

    def __init__(self, app=None):
        """Creates a new RQ object

        :param app: Flask application instance

        """
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        if not self.redis_connection:
            self.set_redis_connection()

    def set_redis_connection(self):
        self.redis_connection = redis.StrictRedis(
            host=self._app.config['RQ_DEFAULT_HOST'],
            port=self._app.config['RQ_DEFAULT_PORT'],
            db=self._app.config['RQ_DEFAULT_DB'])

    def create_queue(self, name=None, **kwargs):
        """Creates a new Queue. Use this instead of rq's `Queue` class.
        This function accepts the same arguments as rq's `Queue` constructor.

        :param name: Queue name. This is used to store a refernence
                     to the queue so you can use RQ.enqueue without
                     having to use the specific queue object.

        """
        kwargs['name'] = self.DEFAULT_QUEUE_NAME if name is None else name
        kwargs['connection'] = self.redis_connection
        self.queues[kwargs['name']] = rq.Queue(**kwargs)
        return self.queues[kwargs['name']]

    def enqueue(self, *args, **kwargs):
        """Enqueues a job. Works very much like RQ's `Queue.enqueue` method
        except that you don't need the actual Queue object.

        :param queue_name: Name of the queue to enqueue on.
                           Defaults to "default".

        """
        queue_name = kwargs.pop('queue_name', self.DEFAULT_QUEUE_NAME)
        return self.queues[queue_name].enqueue(*args, **kwargs)

    def create_worker(self, queues=None):
        """Creates a Worker instance which is bound to the Flask app

        :param queues: A list of queues or queue names for the worker
                       to listen to.
        :returns: A FlaskRQWorker which processes each job in the application
                  context.

        """
        if not queues:
            queues = self.queues.values()

        return FlaskRQWorker(flask_app=self._app,
                             queues=queues,
                             connection=self.redis_connection)


class FlaskRQWorker(rq.Worker):
    def __init__(self, flask_app, *args, **kwargs):
        self._flask_app = flask_app
        return super(FlaskRQWorker, self).__init__(*args, **kwargs)

    def perform_job(self, *args, **kwargs):
        with self._flask_app.app_context():
            return super(FlaskRQWorker, self).perform_job(*args, **kwargs)

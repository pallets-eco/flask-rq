# -*- coding: utf-8 -*-
import unittest

from flask import Flask
from flask_rq import RQ, config_value, get_connection, get_queue, \
    get_server_url, get_worker
from .jobs import simple, specified


class config:
    RQ_LOW_DB = 1
    RQ_HIGH_URL = 'redis://localhost:6379/3'


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    RQ(app)
    return app


class RQTestCase(unittest.TestCase):
    def test_config_default_value_db(self):
        self.assertEqual(config_value('default', 'DB'), 0)

    def test_config_default_value_port(self):
        self.assertEqual(config_value('default', 'PORT'), 6379)

    def test_config_low_value_from_default(self):
        self.assertEqual(config_value('low', 'HOST'), 'localhost')

    def test_config_low_specific_value(self):
        self.assertEqual(config_value('low', 'DB'), 1)

    def test_get_connection_default(self):
        connection = get_connection()
        connection_kwargs = connection.connection_pool.connection_kwargs
        self.assertEqual(connection_kwargs.get('host'), 'localhost')
        self.assertEqual(connection_kwargs.get('port'), 6379)

    def test_connection_from_url(self):
        connection = get_connection('high')
        connection_kwargs = connection.connection_pool.connection_kwargs
        self.assertEqual(connection_kwargs.get('host'), 'localhost')
        self.assertEqual(connection_kwargs.get('port'), 6379)
        self.assertEqual(connection_kwargs.get('db'), 3)

    def test_get_queue_default(self):
        self.assertEqual(get_queue().name, 'default')

    def test_job_default(self):
        simple.delay(0)
        self.assertEqual(len(get_queue().jobs), 1)
        get_worker().work(True)

    def test_job_specified_queue(self):
        specified.delay(3)
        self.assertEqual(len(get_queue('low').jobs), 1)
        get_worker('low').work(True)

    def test_get_server_url_default(self):
        self.assertEqual(get_server_url('high'), 'redis://localhost:6379')

    def test_get_server_url_from_dsn(self):
        self.assertEqual(get_server_url('high'), 'redis://localhost:6379')

    def test_get_worker_default(self):
        worker = get_worker()
        self.assertEqual(worker.queues[0].name, 'default')

    def test_get_worker_low(self):
        worker = get_worker('low')
        self.assertEqual(worker.queues[0].name, 'low')

    def setUp(self):
        self.app = create_app()
        self._ctx = self.app.test_request_context()
        self._ctx.push()


if __name__ == '__main__':
    unittest.main()

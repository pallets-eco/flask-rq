# -*- coding: utf-8 -*-
import unittest

from flask import Flask, current_app
from flask.ext.rq import RQ, config_value, get_connection, get_queue, task


def create_app():
    app = Flask(__name__)
    RQ(app)
    return app


class RQTestCase(unittest.TestCase):
    def test_config_value_db(self):
        self.assertEqual(config_value('default', 'DB'), 0)

    def test_config_value_port(self):
        self.assertEqual(config_value('default', 'PORT'), 6379)

    def test_get_connection_default(self):
        connection = get_connection()
        connection_kwargs = connection.connection_pool.connection_kwargs
        self.assertEqual(connection_kwargs.get('host'), 'localhost')
        self.assertEqual(connection_kwargs.get('port'), 6379)

    def test_get_queue_default(self):
        self.assertEqual(get_queue().name, 'default')

    def test_task_default(self):
        @task
        def job(i):
            return i + 1

        result = job.delay()
        self.assertEqual(len(get_queue().jobs), 1)

    def test_task_default_specified_queue(self):
        @task('low')
        def job(i):
            return i + 1

        result = job.delay()
        self.assertEqual(len(get_queue('low').jobs), 1)

    def setUp(self):
        self.app = create_app()
        self._ctx = self.app.test_request_context()
        self._ctx.push()


if __name__ == '__main__':
    unittest.main()

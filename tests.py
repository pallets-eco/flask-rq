# -*- coding: utf-8 -*-
import unittest

from flask import Flask, current_app
from flask.ext.rq import RQ, config_value


def create_app():
    app = Flask(__name__)
    RQ(app)
    return app


class RQTestCase(unittest.TestCase):
    def test_config_value_db(self):
        self.assertEqual(config_value('default', 'DB'), 0)

    def test_config_value_port(self):
        self.assertEqual(config_value('default', 'PORT'), 6379)

    def setUp(self):
        self.app = create_app()
        self._ctx = self.app.test_request_context()
        self._ctx.push()


if __name__ == '__main__':
    unittest.main()

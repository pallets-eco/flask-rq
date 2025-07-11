from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask
from redis import Redis

from flask_rq import RQ


@pytest.mark.usefixtures("app_ctx")
def test_queues_unset(app: Flask) -> None:
    """When RQ_QUEUES is not set, default queue is added."""
    del app.config["RQ_QUEUES"]
    rq = RQ(app)
    assert list(rq.queues) == ["default"]
    assert rq.queue


@pytest.mark.usefixtures("app_ctx")
def test_queues_no_default(app: Flask) -> None:
    """When RQ_QUEUES is set, default queue is not added."""
    app.config["RQ_QUEUES"] = ["high", "low"]
    rq = RQ(app)
    assert (list(rq.queues)) == ["high", "low"]

    with pytest.raises(KeyError, match="get_queue"):
        assert rq.queue and False

    with pytest.raises(KeyError, match="not configured"):
        assert rq.get_queue() and False


def test_no_testing_yes_async() -> None:
    """Queue.is_async is True if app.testing is False."""
    app = Flask(__name__)
    rq = RQ(app)

    with app.app_context():
        assert rq.queue.is_async


def test_yes_testing_no_async() -> None:
    """Queue.is_async is False if app.testing is True."""
    app = Flask(__name__)
    app.testing = True
    rq = RQ(app)

    with app.app_context():
        assert not rq.queue.is_async


def test_config_async() -> None:
    """Queue.is_async is set by config instead of app.testing."""
    app = Flask(__name__)
    app.testing = True
    app.config["RQ_ASYNC"] = True
    rq = RQ(app)

    with app.app_context():
        assert rq.queue.is_async


def test_default_connection(app: Flask) -> None:
    """Default queue uses config instead of default values."""
    app.config["RQ_CONNECTION"] = {"port": 24242}
    rq = RQ(app)

    with app.app_context():
        assert rq.queue.connection.get_connection_kwargs()["port"] == 24242


@pytest.mark.usefixtures("app_ctx")
def test_connections(rq: RQ) -> None:
    assert rq.queue.connection is not rq.queues["low"].connection
    assert rq.queue.connection is not rq.queues["high"].connection
    assert rq.queue.connection is rq.queues["plain"].connection
    assert rq.queues["low"].connection is not rq.queues["high"].connection
    assert rq.queues["low"].connection is rq.queues["share_low"].connection


def test_bad_forward_ref(app: Flask) -> None:
    app.config["RQ_QUEUES"].append("bad")
    app.config["RQ_QUEUE_CONNECTIONS"]["bad"] = "nothing"

    with pytest.raises(RuntimeError, match=r'\'RQ_QUEUE_CONNECTIONS\["nothing"\]'):
        RQ(app)


def test_connection_class(app: Flask) -> None:
    conn_cls = MagicMock(spec=Redis)
    app.config["RQ_CONNECTION_CLASS"] = conn_cls
    RQ(app)
    assert conn_cls.call_count == 2
    assert conn_cls.from_url.call_count == 1

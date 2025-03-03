from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask
from redis import Redis

from flask_rq import RQ


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


def test_default(app: Flask) -> None:
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


def test_new_preferred(app: Flask) -> None:
    """New config is preferred over old config, shows warning."""
    app.config["RQ_LOW_DB"] = 4

    with pytest.warns(DeprecationWarning, match="The config format has changed"):
        rq = RQ(app)

    with app.app_context():
        assert rq.queues["low"].connection.get_connection_kwargs()["db"] == 1


def test_old_unknown(app: Flask) -> None:
    """Old config handler doesn't warn on unknown keys."""
    app.config["RQ_UNKNOWN"] = "here"
    RQ(app)

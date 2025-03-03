from __future__ import annotations

import typing as t
from pkgutil import resolve_name

import pytest
from flask import Flask

from flask_rq import RQ
from flask_rq._old import get_queue
from flask_rq._old import get_worker
from flask_rq._old import job


@pytest.fixture
def config(redis_port: int) -> dict[str, t.Any]:
    return {
        "TESTING": True,
        "RQ_DEFAULT_PORT": redis_port,
        "RQ_LOW_PORT": redis_port,
        "RQ_LOW_DB": 1,
        "RQ_HIGH_URL": f"redis://localhost:{redis_port}/2",
        "RQ_MULTI_URL": f"redis://localhost:{redis_port}",
        "RQ_MULTI_DB": 3,
        "RQ_BASIC_URL": f"redis://localhost:{redis_port}",
    }


@pytest.fixture
def rq(app: Flask) -> RQ:
    with pytest.warns(DeprecationWarning, match="The config format has changed"):
        rq = RQ(app)

    return rq


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_default(rq: RQ) -> None:
    queue = get_queue()
    assert queue.name == "default"
    assert queue.connection.get_connection_kwargs()["db"] == 0
    assert queue is rq.queue


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_db(rq: RQ) -> None:
    queue = get_queue("low")
    assert queue.connection.get_connection_kwargs()["db"] == 1
    assert queue is rq.queues["low"]


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_url(rq: RQ) -> None:
    queue = get_queue("high")
    assert queue.connection.get_connection_kwargs()["db"] == 2
    assert queue is rq.queues["high"]


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_url_no_db(rq: RQ) -> None:
    queue = get_queue("basic")
    assert queue.connection.get_connection_kwargs()["db"] == 0
    assert queue is rq.queues["basic"]


@pytest.mark.usefixtures("app_ctx", "rq")
def test_get_queue_combine() -> None:
    queue = get_queue("multi")
    assert queue.connection.get_connection_kwargs()["db"] == 3


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_custom(rq: RQ) -> None:
    queue = get_queue(is_async=False)
    assert queue.name == "default"
    assert not queue.is_async
    assert queue is not rq.queue
    assert queue.connection is rq.queue.connection


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_custom_connection(rq: RQ) -> None:
    queue = get_queue(connection=rq.queues["low"].connection)
    assert queue.name == "default"
    assert queue is not rq.queue
    assert queue.connection is rq.queues["low"].connection


@pytest.mark.usefixtures("app_ctx")
def test_get_queue_custom_default_connection(rq: RQ) -> None:
    queue = get_queue("other")
    assert queue.name == "other"
    assert "other" not in rq.queues
    assert queue.connection == rq.queue.connection


@pytest.mark.usefixtures("app_ctx")
def test_get_worker_default(rq: RQ) -> None:
    worker = get_worker()
    assert len(worker.queues) == 5
    assert worker.queues[0].name == "default"
    assert worker.connection is rq.queue.connection


@pytest.mark.usefixtures("app_ctx")
def test_get_worker_queues(rq: RQ) -> None:
    worker = get_worker("low", "high")
    assert len(worker.queues) == 2
    assert worker.queues[0].name == "low"
    assert worker.connection is rq.queues["low"].connection


def mul(a: int, b: int) -> int:
    return a * b


@pytest.mark.usefixtures("app_ctx")
def test_job_default(rq: RQ) -> None:
    job_mul = job(mul)
    j = job_mul.enqueue(6, 7)
    assert j.origin == "default"
    r = j.latest_result()
    assert r is not None
    assert r.return_value == 42


@pytest.mark.usefixtures("app_ctx")
def test_job_low(rq: RQ) -> None:
    job_mul = job("low")(mul)
    j = job_mul.enqueue(4, 8)
    assert j.origin == "low"
    r = j.latest_result()
    assert r is not None
    assert r.return_value == 32


def test_no_app() -> None:
    with pytest.raises(RuntimeError, match="Working outside of application context"):
        get_queue()


@pytest.mark.usefixtures("app_ctx")
def test_no_ext() -> None:
    with pytest.raises(RuntimeError, match="The current app is not registered"):
        get_queue()


@pytest.mark.parametrize("name", ["__version__", "get_queue", "get_worker", "job"])
def test_import_deprecated(name: str) -> None:
    with pytest.warns(DeprecationWarning):
        resolve_name(f"flask_rq:{name}")

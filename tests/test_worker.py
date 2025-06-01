from __future__ import annotations

import typing as t

import pytest
from flask import current_app as flask_current_app
from flask import Flask
from quart import current_app as quart_current_app
from quart import Quart

from flask_rq import RQ


@pytest.fixture
def config(config: dict[str, t.Any]) -> dict[str, t.Any]:
    config["FIND"] = "found"
    config["RQ_ASYNC"] = True
    return config


def flask_sync_job() -> str:  # pragma: no cover
    return flask_current_app.config["FIND"]  # type: ignore[no-any-return]


async def flask_async_job() -> str:  # pragma: no cover
    return flask_current_app.config["FIND"]  # type: ignore[no-any-return]


@pytest.mark.parametrize("func", [flask_sync_job, flask_async_job])
def test_flask(app: Flask, rq: RQ, func: t.Callable[[], str]) -> None:
    with app.app_context():
        job = rq.queue.enqueue(func)
        worker = rq.make_worker()

    worker.work(burst=True)
    r = job.latest_result()
    assert r is not None
    assert r.return_value == "found"


async def quart_async_job() -> str:  # pragma: no cover
    return quart_current_app.config["FIND"]  # type: ignore[no-any-return]


def quart_sync_job() -> str:  # pragma: no cover
    return quart_current_app.config["FIND"]  # type: ignore[no-any-return]


@pytest.mark.parametrize("func", [quart_async_job, quart_sync_job])
async def test_quart(quart_app: Quart, rq: RQ, func: t.Callable[[], str]) -> None:
    async with quart_app.app_context():
        job = rq.queue.enqueue(func)
        worker = rq.make_worker()

    worker.work(burst=True)
    r = job.latest_result()
    assert r is not None
    assert r.return_value == "found"


@pytest.mark.usefixtures("app_ctx")
def test_worker_no_arg(rq: RQ) -> None:
    worker = rq.make_worker()
    assert len(worker.queues) == 5
    assert worker.connection is rq.queue.connection


@pytest.mark.usefixtures("app_ctx")
def test_worker_default_first(rq: RQ) -> None:
    worker = rq.make_worker(["default", "high"])
    assert len(worker.queues) == 2
    assert worker.connection == rq.queue.connection


@pytest.mark.usefixtures("app_ctx")
def test_worker_default_second(rq: RQ) -> None:
    worker = rq.make_worker(["high", "default"])
    assert len(worker.queues) == 2
    assert worker.connection == rq.queues["high"].connection


@pytest.mark.usefixtures("app_ctx")
def test_worker_no_default(rq: RQ) -> None:
    worker = rq.make_worker(["low", "high"])
    assert len(worker.queues) == 2
    assert worker.connection is rq.queues["low"].connection

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
def test_worker_default(rq: RQ) -> None:
    worker = rq.make_worker()
    assert len(worker.queues) == 5
    assert worker.connection is rq.queues["default"].connection


@pytest.mark.usefixtures("app_ctx")
def test_worker_queues(rq: RQ) -> None:
    worker = rq.make_worker(["low", "high"])
    assert len(worker.queues) == 2
    assert worker.connection is rq.queues["low"].connection


class TestConfigQueueOrderBase:
    config_queue = []
    config_queue_connections = {}
    param_queue_default_provided_first = ["default", "high"]
    param_queue_default_provided = ["high", "default"]
    param_queue_default_not_provided = ["high", "low"]

    @pytest.fixture
    def config(self, config: dict[str, t.Any], redis_port: int) -> dict[str, t.Any]:
        reference_connections = {
            "low": {"port": redis_port, "db": 1},
            "high": f"redis://localhost:{redis_port}/2",
            "share_low": "low",
            "plain": None,
        }
        self.config_queue_connections = {
            key: value
            for key, value in reference_connections.items()
            if key in self.config_queue
        }

        config["RQ_QUEUES"] = self.config_queue
        print(config["RQ_QUEUES"])
        config["RQ_QUEUE_CONNECTIONS"] = self.config_queue_connections
        print(config["RQ_QUEUE_CONNECTIONS"])
        return config

    @pytest.mark.usefixtures("app_ctx")
    def test_worker_no_param(self, rq: RQ) -> None:
        worker = rq.make_worker()
        assert (
            worker.queue_names() == self.config_queue
            if self.config_queue != []
            else ["default"]
        )
        assert worker.connection is rq.queues["default"].connection

    @pytest.mark.usefixtures("app_ctx")
    def test_worker_param_default_provided(self, rq: RQ) -> None:
        worker = rq.make_worker(self.param_queue_default_provided)
        assert worker.queue_names() == self.param_queue_default_provided
        assert worker.connection is rq.queues["default"].connection

    @pytest.mark.usefixtures("app_ctx")
    def test_worker_param_default_provided_first(self, rq: RQ) -> None:
        worker = rq.make_worker(self.param_queue_default_provided_first)
        assert worker.queue_names() == self.param_queue_default_provided_first
        assert worker.connection is rq.queues["default"].connection

    @pytest.mark.usefixtures("app_ctx")
    def test_worker_param_default_not_provided(self, rq: RQ) -> None:
        worker = rq.make_worker(self.param_queue_default_not_provided)
        assert worker.queue_names() == self.param_queue_default_not_provided
        assert (
            worker.connection
            is rq.queues[self.param_queue_default_not_provided[0]].connection
        )


class TestConfigQueueDefaultProvidedFirst(TestConfigQueueOrderBase):
    config_queue = ["default", "high", "low"]


class TestConfigQueueDefaultPresentNotFirst(TestConfigQueueOrderBase):
    config_queue = ["high", "default", "low"]


class TestConfigQueueDefaultNotPresent(TestConfigQueueOrderBase):
    config_queue = ["high", "low"]

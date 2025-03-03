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
    return config


def flask_sync_job() -> str:  # pragma: no cover
    return flask_current_app.config["FIND"]  # type: ignore[no-any-return]


async def flask_async_job() -> str:  # pragma: no cover
    return flask_current_app.config["FIND"]  # type: ignore[no-any-return]


@pytest.mark.parametrize("func", [flask_sync_job, flask_async_job])
def test_flask(app: Flask, rq: RQ, func: t.Callable[[], str]) -> None:
    with app.app_context():
        job = rq.queue.create_job(func)

    assert job.perform() == "found"


async def quart_async_job() -> str:  # pragma: no cover
    return quart_current_app.config["FIND"]  # type: ignore[no-any-return]


def quart_sync_job() -> str:  # pragma: no cover
    return quart_current_app.config["FIND"]  # type: ignore[no-any-return]


@pytest.mark.parametrize("func", [quart_async_job, quart_sync_job])
async def test_quart(quart_app: Quart, rq: RQ, func: t.Callable[[], str]) -> None:
    async with quart_app.app_context():
        job = rq.queue.create_job(func)

    job_func = job.func
    assert job_func is not None
    assert await job_func() == "found"

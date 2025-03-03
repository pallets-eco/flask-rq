from __future__ import annotations

import collections.abc as cabc
import subprocess
import time
import typing as t

import ephemeral_port_reserve
import pytest
from flask import Flask
from quart import Quart
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from flask_rq import RQ


@pytest.fixture(scope="session")
def redis_port() -> int:
    return ephemeral_port_reserve.reserve()  # type: ignore[no-any-return]


@pytest.fixture(scope="session", autouse=True)
def _start_redis(
    tmp_path_factory: pytest.TempPathFactory, redis_port: int
) -> cabc.Iterator[None]:
    proc = subprocess.Popen(
        ["redis-server", "--port", str(redis_port)],
        cwd=tmp_path_factory.mktemp("redis-server"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    while True:
        try:
            redis = Redis(port=redis_port, single_connection_client=True)
            redis.ping()
            break
        except (ConnectionError, RedisConnectionError):  # pragma: no cover
            time.sleep(0.1)

    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(autouse=True)
def _reset_redis(redis_port: int) -> cabc.Iterator[None]:
    yield
    Redis(port=redis_port, single_connection_client=True).flushall()


@pytest.fixture
def config(redis_port: int) -> dict[str, t.Any]:
    return {
        "TESTING": True,
        "RQ_CONNECTION": {"port": redis_port},
        "RQ_QUEUES": ["low", "high", "share_low", "plain"],
        "RQ_QUEUE_CONNECTIONS": {
            "low": {"port": redis_port, "db": 1},
            "high": f"redis://localhost:{redis_port}/2",
            "share_low": "low",
            "plain": None,
        },
    }


@pytest.fixture
def app(config: dict[str, t.Any]) -> Flask:
    app = Flask(__name__)
    app.config |= config
    return app


@pytest.fixture
def app_ctx(app: Flask) -> cabc.Iterator[None]:
    with app.app_context():
        yield


@pytest.fixture
def quart_app(config: dict[str, t.Any]) -> Quart:
    app = Quart(__name__)
    app.config |= config
    return app


@pytest.fixture
def rq(app: Flask, quart_app: Quart) -> RQ:
    rq = RQ()
    rq.init_app(app)
    rq.init_app(quart_app)
    return rq

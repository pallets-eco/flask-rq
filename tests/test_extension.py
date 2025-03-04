from __future__ import annotations

import pytest
from flask import Flask
from quart import Quart

from flask_rq import RQ


def test_init(app: Flask) -> None:
    rq = RQ(app)

    with app.app_context():
        assert len(rq.queues) == 5


def test_init_app(app: Flask) -> None:
    rq = RQ()
    rq.init_app(app)

    with app.app_context():
        assert len(rq.queues) == 5


def test_init_twice(app: Flask) -> None:
    rq = RQ(app)

    with pytest.raises(RuntimeError, match="An RQ extension is already"):
        rq.init_app(app)


async def test_init_quart(quart_app: Quart) -> None:
    rq = RQ(quart_app)

    async with quart_app.app_context():
        assert len(rq.queues) == 5


def test_no_context(rq: RQ) -> None:
    with pytest.raises(RuntimeError, match="Working outside of application context"):
        assert rq.queues


@pytest.mark.usefixtures("app_ctx")
def test_no_init() -> None:
    rq = RQ()

    with pytest.raises(RuntimeError, match="No applications are registered"):
        assert rq.queues


def test_other_init(rq: RQ) -> None:
    app = Flask(__name__)

    with app.app_context():
        with pytest.raises(
            RuntimeError, match="The current application is not registered"
        ):
            assert rq.queues

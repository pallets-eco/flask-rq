from __future__ import annotations

import typing as t
from unittest.mock import Mock
from unittest.mock import patch

import click
import pytest
from flask import Flask
from flask.globals import app_ctx
from rq.cli import cli as orig_cli

from flask_rq import RQ
from flask_rq._cli import from_rq_cmd


def test_ctx_obj(app: Flask, rq: RQ) -> None:
    recorded_app: t.Any | None = None
    recorded_obj: t.Any | None = None
    group = t.cast(click.Group, app.cli.commands["rq"])

    @group.command()
    @click.pass_obj
    def record(obj: t.Any) -> None:
        nonlocal recorded_app
        nonlocal recorded_obj
        recorded_app = app_ctx.app
        recorded_obj = obj

    runner = app.test_cli_runner()
    runner.invoke(args=["rq", "record"])
    assert recorded_app is app
    assert recorded_obj is rq


def test_from_rq_cmd() -> None:
    @from_rq_cmd(orig_cli.worker, {"queues"})
    def worker(**kwargs: t.Any) -> None:  # pragma: no cover
        pass

    assert worker.__doc__ == orig_cli.worker.__doc__
    assert worker.__click_params__[0].name == "queues"  # type: ignore[attr-defined]


def test_from_rq_cmd_override_doc() -> None:
    @from_rq_cmd(orig_cli.worker, {"queues"})
    def worker(**kwargs: t.Any) -> None:  # pragma: no cover
        """override"""

    assert worker.__doc__ == "override"


@pytest.mark.usefixtures("rq")
@patch("flask_rq._extension.Worker", spec=True)
def test_worker(worker_cls: Mock, app: Flask) -> None:
    runner = app.test_cli_runner()
    runner.invoke(args=["rq", "worker"])
    worker_cls.assert_called()
    assert "default_result_ttl" in worker_cls.call_args.kwargs
    worker: Mock = worker_cls.return_value
    work: Mock = worker.work
    work.assert_called()
    assert "burst" in work.call_args.kwargs

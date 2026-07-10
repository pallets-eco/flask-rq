from __future__ import annotations

import typing as t

import pytest
from flask import Flask
from rq import cron

from flask_rq import RQ


def job1(n: int = 1) -> None: ...


@pytest.mark.parametrize(
    ("conn_conf", "port"),
    [("redis://localhost:24241", 24241), ({"port": 24242}, 24242)],
)
def test_make_scheduler(
    app: Flask, conn_conf: str | dict[str, t.Any], port: int
) -> None:
    """Scheduler uses app config and default connection."""
    app.config["RQ_CONNECTION"] = conn_conf
    rq = RQ(app)

    with app.app_context():
        scheduler = rq.make_cron_scheduler()

    assert scheduler.name == app.name
    assert scheduler.connection.get_connection_kwargs()["port"] == port


@pytest.mark.usefixtures("app_ctx")
def test_global_register(request: pytest.FixtureRequest, rq: RQ) -> None:
    """Global register is added to the scheduler."""
    request.addfinalizer(lambda: cron._job_data_registry.clear())
    cron.register(job1, "default", interval=10)
    cron.register(job1, "low", cron="* * * * 1")
    scheduler = rq.make_cron_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    assert jobs[0].interval == 10
    assert jobs[1].cron == "* * * * 1"


@pytest.mark.usefixtures("app_ctx")
def test_instance_register(rq: RQ) -> None:
    """Instance register is added to the scheduler."""
    rq.cron_register(job1, 20, kwargs={"n": 2})
    rq.cron_register(job1, "* * * * 2", queue="low", args=(3,))
    scheduler = rq.make_cron_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    assert jobs[0].queue_name == "default"
    assert jobs[0].interval == 20
    assert jobs[0].kwargs["n"] == 2
    assert jobs[1].queue_name == "low"
    assert jobs[1].cron == "* * * * 2"
    assert jobs[1].args[0] == 3


@pytest.mark.usefixtures("app_ctx")
def test_wrapper_register(rq: RQ) -> None:
    """Wrapper register is added to the scheduler."""
    wrapped_job1 = rq.job(job1)
    wrapped_job1.cron_register(30, n=4)
    scheduler = rq.make_cron_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].func == job1
    assert jobs[0].queue_name == "default"
    assert jobs[0].interval == 30
    assert jobs[0].kwargs["n"] == 4

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from rq.executions import Execution

from flask_rq import RQ
from flask_rq._worker import FlaskSubprocessWorker
from flask_rq._worker import run_work_horse


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


@pytest.mark.parametrize(
    ("argv", "expect"),
    [
        (["/tmp/flask", "rq", "worker"], ["/tmp/flask"]),
        (["-m", "flask", "rq", "worker"], ["-m", "flask"]),
        (["script.py"], ["-m", "flask"]),
    ],
)
@pytest.mark.usefixtures("app_ctx")
def test_fork(rq: RQ, argv: list[str], expect: list[str]) -> None:
    worker = rq.make_worker()
    assert isinstance(worker, FlaskSubprocessWorker)
    job = MagicMock(spec=rq.queue.job_class)
    job.id = "job-test"
    execution = MagicMock(spec=Execution)
    execution.id = "execution-test"
    worker.execution = execution

    with (
        patch.object(sys, "orig_argv", ["python", *argv]),
        patch.dict(os.environ, {"FLASK_APP": "test"}),
        patch("subprocess.Popen", spec=True) as mock_popen,
        patch.object(worker, "procline"),
    ):
        mock_popen.return_value.pid = 50
        worker.fork_work_horse(job, rq.queue)

    assert mock_popen.call_args is not None
    assert mock_popen.call_args.args[0] == [
        sys.executable,
        *expect,
        "rq",
        "work-horse",
        "default",
        worker.key,
        "job-test",
        "execution-test",
    ]
    assert worker._horse_pid == 50


@pytest.mark.usefixtures("app_ctx")
def test_fork_no_app(rq: RQ) -> None:
    worker = rq.make_worker()
    assert isinstance(worker, FlaskSubprocessWorker)

    with (
        pytest.raises(RuntimeError, match="FLASK_APP"),
        patch.object(sys, "orig_argv", ["python", "script.py"]),
    ):
        worker.fork_work_horse(None, None)  # type: ignore[arg-type]


@pytest.mark.usefixtures("app_ctx")
def test_run_work_horse(rq: RQ) -> None:
    queue = rq.queue
    worker = MagicMock(spec=FlaskSubprocessWorker)
    job = MagicMock(spec=queue.job_class)
    execution = MagicMock(spec=Execution)

    with (
        patch.object(FlaskSubprocessWorker, "find_by_key", return_value=worker),
        patch.object(queue, "fetch_job", return_value=job),
        patch.object(Execution, "fetch", return_value=execution),
    ):
        run_work_horse(
            rq_ext=rq,
            queue_name="default",
            worker_key="worker-test",
            job_id="job-test",
            execution_id="execution-test",
        )

    assert worker.execution is execution
    assert worker._is_horse
    worker.main_work_horse.assert_called_once_with(job, queue)

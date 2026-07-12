from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import typing as t

from rq import Worker
from rq.executions import Execution
from rq.job import Job
from rq.queue import Queue
from rq.worker import SHUTDOWN_SIGNAL

if t.TYPE_CHECKING:
    from ._extension import RQ


class FlaskSubprocessWorker(Worker):
    """Start a subprocess with the ``flask`` CLI to run a job."""

    _horse_proc: subprocess.Popen[bytes] | None = None

    @property
    def horse_proc(self) -> subprocess.Popen[bytes]:
        return self._horse_proc  # type: ignore[return-value]

    @horse_proc.setter
    def horse_proc(self, value: subprocess.Popen[bytes]) -> None:
        self._horse_proc = value
        self._horse_pid = value.pid

    def fork_work_horse(self, job: Job, queue: Queue) -> None:
        # Find args leading up to the "rq" command.
        for i, arg in enumerate(sys.orig_argv):
            if arg == "rq":
                rq_argv = sys.orig_argv[1 : i + 1]
                break
        else:
            # Worker started from a script, not the ``flask rq`` command.
            # Require FLASK_APP to load the app.
            if "FLASK_APP" not in os.environ:
                raise RuntimeError(
                    "'FLASK_APP' env var must be set when not using 'flask' CLI."
                )

            rq_argv = ["-m", "flask", "rq"]

        if sys.platform != "win32":
            flags = 0
        else:  # pragma: no cover
            flags = subprocess.CREATE_NEW_PROCESS_GROUP

        assert self.execution is not None
        self.horse_proc = subprocess.Popen(
            [
                sys.executable,
                *rq_argv,
                "work-horse",
                queue.name,
                self.key,
                job.id,
                self.execution.id,
            ],
            env=os.environ,
            process_group=0,
            creationflags=flags,
        )
        self.procline(f"Started {self.horse_proc.pid} at {time.time()}")  # type: ignore[no-untyped-call]

    def wait_for_horse(
        self,
    ) -> tuple[int, int, t.Any] | tuple[None, None, None]:  # pragma: no cover
        try:
            if sys.platform != "win32":
                import resource

                rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
            else:
                rusage = None

            code = self.horse_proc.wait()
            return self.horse_pid, code, rusage
        except ChildProcessError:
            return None, None, None

    def kill_horse(
        self, sig: signal.Signals = SHUTDOWN_SIGNAL
    ) -> None:  # pragma: no cover
        try:
            self.horse_proc.send_signal(sig)
            self.log.info(f"Worker {self.name}: sent {sig.name} to {self.horse_pid}")
        except ProcessLookupError:
            self.log.debug(f"Worker {self.name}: {self.horse_pid} is dead")


def run_work_horse(
    rq_ext: RQ,
    queue_name: str,
    worker_key: str,
    job_id: str,
    execution_id: str,
) -> None:
    """Recreate the worker and job execution in the subprocess. This is similar
    to the code ``SpawnWorker`` passes to ``os.spawnv``.
    """
    queue = rq_ext.get_queue(queue_name)
    assert queue.connection is not None
    worker = FlaskSubprocessWorker.find_by_key(
        worker_key,
        connection=queue.connection,
        job_class=queue.job_class,
        queue_class=queue.__class__,
        serializer=queue.serializer,
    )
    assert worker is not None
    job = queue.fetch_job(job_id)
    assert job is not None
    worker.execution = Execution.fetch(
        execution_id, job_id, connection=queue.connection
    )
    worker._is_horse = True
    worker.main_work_horse(job, queue)

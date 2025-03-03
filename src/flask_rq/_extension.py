from __future__ import annotations

import typing as t
from weakref import WeakKeyDictionary

import typing_extensions as te
from flask import Flask
from flask.globals import app_ctx as flask_app_ctx
from rq import Queue
from rq import Worker

from ._cli import make_cli
from ._job_wrapper import JobWrapper
from ._make import make_queues

if t.TYPE_CHECKING:
    from quart import Quart

P = te.ParamSpec("P")
R = t.TypeVar("R")


class RQ:
    """Manage RQ queues and Redis connections for Flask and Quart applications.

    :param app: Call :meth:`init_app` with this application.
    """

    def __init__(self, app: Flask | Quart | None = None) -> None:
        self._queues: WeakKeyDictionary[Flask | Quart, dict[str, Queue]] = (
            WeakKeyDictionary()
        )
        self._flask_ctx: t.Any = None
        self._quart_ctx: t.Any = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask | Quart) -> None:
        """Register the extension on an application, creating queues from its
        :attr:`~.Flask.config`.

        :param app: The application to register.
        """
        if "rq" in app.extensions:
            raise RuntimeError(
                "An RQ extension is already initialized on this application."
                " Import and use that instead."
            )

        if isinstance(app, Flask):
            self._flask_ctx = flask_app_ctx
        else:
            from quart.globals import app_ctx

            self._quart_ctx = app_ctx

        self._queues[app] = make_queues(app)
        app.extensions["rq"] = self
        make_cli(app)

    def _get_current_app(self) -> Flask | Quart:
        """Get the current app, ensuring it has been registered with this
        extension instance. Flask and Quart use separate `app_ctx` globals, so
        the extension records which types of apps have been registered in order
        to know what to check.
        """
        app: Flask | Quart

        if self._flask_ctx is None and self._quart_ctx is None:
            raise RuntimeError("No applications are registered with this RQ extension.")

        if self._flask_ctx:
            app = self._flask_ctx.app
        elif self._quart_ctx:
            app = self._quart_ctx.app
        else:
            raise RuntimeError(
                "Working outside of application context. This must be used in"
                " a view, CLI command, or app.app_context() block."
            )

        if app not in self._queues:
            raise RuntimeError(
                "The current application is not registered with this RQ extension."
            )

        return app

    @property
    def queues(self) -> dict[str, Queue]:
        """The queues associated with the current application."""
        return self._queues[self._get_current_app()]

    def get_queue(self, name: str = "default") -> Queue:
        """Get a specific queue associated with the current application.

        The :attr:`queue` attribute is a shortcut for calling this without an
        argument to get the default queue.

        :param name: The name associated with the queue.
        """
        return self.queues[name]

    @property
    def queue(self) -> Queue:
        """The default queue associated with the current application."""
        return self.get_queue()

    def make_worker(
        self, queues: list[str] | tuple[str, ...] | None = None, **kwargs: t.Any
    ) -> Worker:
        """Create a worker for the current application that will watch the
        configured queues and execute jobs in the application context.

        :param queues: The named queues for the worker to watch, using the first
            queue's connection. By default, watches all the configured queues
            using the default queue's connection.
        :param kwargs: Other arguments to pass to the worker constructor.
        """
        app = self._get_current_app()
        known_queues = self._queues[app]
        worker_queues: list[Queue] = []

        if not queues:
            known_queues = known_queues.copy()
            # Default queue is first so its connection is used.
            worker_queues.append(known_queues.pop("default"))
            worker_queues.extend(known_queues.values())
        else:
            worker_queues.extend(known_queues[k] for k in queues)

        return Worker(worker_queues, job_class=worker_queues[0].job_class, **kwargs)

    @t.overload
    def job(self, f: t.Callable[P, R], *, queue: str = ...) -> JobWrapper[P, R]: ...

    @t.overload
    def job(
        self, *, queue: str = ...
    ) -> t.Callable[[t.Callable[P, R]], JobWrapper[P, R]]: ...

    def job(
        self,
        f: t.Callable[P, R] | None = None,
        *,
        queue: str = "default",
    ) -> JobWrapper[P, R] | t.Callable[[t.Callable[P, R]], JobWrapper[P, R]]:
        """Wrap the decorated function to add an `enqueue` method to it.
        `job.enqueue()` is a shortcut for `rq.queue.enqueue(job)`. Can be
        used as a decorator with or without arguments, or as a function.

        .. code-block:: python

            @rq.job
            def add(a, b):
                return a + b

            @rq.job(queue="math")
            def sub(a, b):
                return a - b

            mul = rq.job(lambda a, b: a * b, queue="math")

        :param f: The job function. If not given, return a new decorator that
            uses the other given arguments.
        :param queue: The queue to use to submit this job.
        """
        if f is not None:
            return JobWrapper(rq=self, queue=queue, func=f)

        def decorator(f: t.Callable[P, R]) -> JobWrapper[P, R]:
            return self.job(f, queue=queue)

        return decorator

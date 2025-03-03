from __future__ import annotations

import typing as t

import redis
import typing_extensions as te
from flask.globals import app_ctx as flask_app_ctx
from rq import Queue
from rq import Worker

from ._extension import RQ
from ._job_wrapper import JobWrapper

P = te.ParamSpec("P")
R = t.TypeVar("R")


def get_connection(queue: str = "default") -> redis.Redis:
    """Get the Redis connection for the given queue. If the queue does not
    exist, use the default queue's connection instead.

    :param queue: The name of the queue to get the connection from.

    .. deprecated:: 0.3
        Will be removed in Flask-RQ 1.0. Use ``rq.get_queue().connection``
        instead.
    """
    rq_ext = _get_current_ext()
    queues = rq_ext.queues

    if queue in queues:
        return queues[queue].connection

    return queues["default"].connection


def get_queue(name: str = "default", **kwargs: t.Any) -> Queue:
    """Get the RQ queue with the given name.

    If other arguments are given, create a new queue instance instead of using
    an existing queue. If the named queue exists, use its connection.

    :param name: The name of the queue to get.
    :param kwargs: Create a new queue instance with these arguments.

    .. deprecated:: 0.3
        Will be removed in Flask-RQ 1.0. Use ``rq.get_queue()`` instead.
    """
    rq_ext = _get_current_ext()
    queues = rq_ext.queues

    if kwargs or name not in queues:
        if "connection" not in kwargs:
            kwargs["connection"] = get_connection(name)

        return Queue(name, **kwargs)

    return queues[name]


def get_worker(*queues: str) -> Worker:
    """Get a RQ worker that watches the given queue names.

    :param queues: Names of queues for the worker to watch.

    .. deprecated:: 0.3
        Will be removed in Flask-RQ 1.0. Use ``rq.make_worker()`` instead.
    """
    return _get_current_ext().make_worker(queues)


@t.overload
def job(func_or_queue: t.Callable[P, R]) -> JobWrapper[P, R]: ...


@t.overload
def job(
    func_or_queue: str | None = ...,
) -> t.Callable[[t.Callable[P, R]], JobWrapper[P, R]]: ...


def job(
    func_or_queue: t.Callable[P, R] | str | None = None,
) -> JobWrapper[P, R] | t.Callable[[t.Callable[P, R]], JobWrapper[P, R]]:
    """Wrap the decorated function to add an `enqueue` method to it.
    ``job.enqueue()`` is a shortcut for ``rq.queue.enqueue(job)``.

    :param func_or_queue: A job function to wrap. Or a queue name, returning
        a new decorator.

    .. deprecated:: 0.3
        Will be removed in Flask-RQ 1.0. Use ``rq.job()`` instead. The added
        ``delay`` method is renamed to ``enqueue``.
    """
    rq_ext = _get_current_ext()

    if callable(func_or_queue):
        return rq_ext.job(func_or_queue)

    return rq_ext.job(queue=func_or_queue or "default")


def _get_current_ext() -> RQ:
    """Get the extension instance associated with the current app context."""
    if flask_app_ctx:
        app = flask_app_ctx.app
    else:
        raise RuntimeError(
            "Working outside of application context. This typically"
            " means that you attempted to use functionality that needed"
            " the current application, but were not in a view, CLI"
            " command, or app.app_context() block."
        )

    if "rq" not in app.extensions:
        raise RuntimeError(
            "The current app is not registered with the Flask-RQ extension."
            " This typically means you forgot to call 'init_app', or"
            " created additional 'RQExtension' instances instead of"
            " importing a central one."
        )

    return app.extensions["rq"]  # type: ignore[no-any-return]

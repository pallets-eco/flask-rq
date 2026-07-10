from __future__ import annotations

import typing as t
from datetime import datetime
from datetime import timedelta
from functools import update_wrapper

import typing_extensions as te
from rq.job import Job

if t.TYPE_CHECKING:
    from ._extension import RQ

P = te.ParamSpec("P")
R = t.TypeVar("R")


class JobWrapper(t.Generic[P, R]):
    """Wrap a regular function to add a :meth:`enqueue` method that submits the
    job using the given queue from the given extension instance. The wrapper is
    callable and retains the same type signature.

    This class itself is not part of the public API, only its documented
    methods are.

    :param rq: The RQ extension instance, used to get the queue.
    :param queue: The name of the queue to use when enqueuing the job.
    :param func: The job function.
    """

    def __init__(self, rq: RQ, queue: str, func: t.Callable[P, R]) -> None:
        self.rq: RQ = rq
        """The RQ extension instance used to get the queue.

        :meta private:
        """

        self.queue: str = queue
        """The queue name to enqueue the function on.

        :meta private:
        """

        self.func: t.Callable[P, R] = func
        """The wrapped function.

        This wrapper class cannot be passed to `rq.Queue.enqueue` etc.
        Preferably, use the wrapper's methods instead; pass this if you cannot
        in some situation.
        """

        update_wrapper(self, func)

    def __call__(self, /, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the wrapped function directly.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function.
        """
        return self.func(*args, **kwargs)

    def enqueue(self, /, *args: P.args, **kwargs: P.kwargs) -> Job:
        """Submit the wrapped function to the queue for background execution.
        Calls :meth:`rq.Queue.enqueue`.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function,
            along with any keyword arguments that can be passed to
            ``Queue.enqueue``.
        """
        queue = self.rq.queues[self.queue]
        return queue.enqueue(self.func, *args, **kwargs)

    def enqueue_at(self, when: datetime, /, *args: P.args, **kwargs: P.kwargs) -> Job:
        """Like :meth:`enqueue`, but waits to run the function until the given
        time. Calls :meth:`rq.Queue.enqueue_at`.

        :param when: Wait until this time before running the job.
        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function,
            along with any keyword arguments that can be passed to
            ``Queue.enqueue_at``.
        """
        queue = self.rq.queues[self.queue]
        return queue.enqueue_at(when, self.func, *args, **kwargs)  # type: ignore[no-any-return]

    def enqueue_in(
        self, when: int | float | timedelta, /, *args: P.args, **kwargs: P.kwargs
    ) -> Job:
        """Like :meth:`enqueue`, but waits to run the function until the given
        interval has passed. Calls :meth:`rq.Queue.enqueue_in`.

        :param when: Wait for this interval (seconds or a ``timedelta``) before
            running the job.
        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function,
            along with any keyword arguments that can be passed to
            ``Queue.enqueue_in``.
        """
        if isinstance(when, (int, float)):
            when = timedelta(seconds=when)

        queue = self.rq.queues[self.queue]
        return queue.enqueue_in(when, self.func, *args, **kwargs)

    def cron_register(
        self, interval: int | str, /, *args: P.args, **kwargs: P.kwargs
    ) -> None:
        """Register a Cron schedule for the wrapped function to be periodically
        added to the queue. Calls :meth:`.RQ.cron_register`.

        :param interval: An int number of seconds, or a Cron string, descrbing
            when the job is scheduled.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function.
        """
        self.rq.cron_register(
            self.func, interval, queue=self.queue, args=args, kwargs=kwargs
        )

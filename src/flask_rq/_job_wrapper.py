from __future__ import annotations

import typing as t
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

        :meta private:
        """

        update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Call the wrapped function directly.

        This retains the same static type signature as the wrapped function.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function.
        """
        return self.func(*args, **kwargs)

    def enqueue(self, *args: P.args, **kwargs: P.kwargs) -> Job:
        """Submit the wrapped function to the queue for background execution.

        This retains the same static type signature for as the wrapped function,
        except it returns a :class:`rq.Job` instance.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function,
            along with any keyword arguments that can be passed to
            :meth:`rq.Queue.enqueue`.
        """
        queue = self.rq.queues[self.queue]
        return queue.enqueue(self.func, *args, **kwargs)  # pyright: ignore

    def delay(self, *args: P.args, **kwargs: P.kwargs) -> Job:
        """Submit the wrapped function to the queue for background execution.

        :param args: Any positional arguments accepted by the wrapped function.
        :param kwargs: Any keyword arguments accepted by the wrapped function,
            along with any keyword arguments that can be passed to
            :meth:`rq.Queue.enqueue`.

        .. deprecated:: 0.3
            Renamed to :meth:`enqueue`. Will be removed in Flask-RQ 1.0.
        """
        import warnings

        warnings.warn(
            "The 'delay' method has been renamed to 'enqueue' to match RQ's"
            " terminology. The old name is deprecated and will be removed in"
            " Flask-RQ 1.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.enqueue(*args, **kwargs)

from __future__ import annotations

import typing as t
import weakref
from functools import update_wrapper

from flask import Flask
from rq.job import Job

if t.TYPE_CHECKING:
    from quart import Quart


class FlaskJob(Job):
    """An RQ job class that knows about the current Flask app and executes its
    function inside an active application context.
    """

    _flask_app: weakref.ref[Flask]

    @property
    def func(self) -> t.Any:
        """Wrap the job's function in a sync function that pushes a Flask
        application context. Async functions are also supported, relying on
        Flask's ``ensure_sync`` and asgiref.
        """
        func = t.cast(t.Callable[..., t.Any], super().func)
        app = self._flask_app()
        assert app is not None

        def new_func(*args: t.Any, **kwargs: t.Any) -> t.Any:
            with app.app_context():
                return app.ensure_sync(func)(*args, **kwargs)

        return update_wrapper(new_func, func)


class QuartJob(Job):
    """An RQ job class that knows about the current Quart app and executes its
    function inside an active application context.
    """

    _quart_app: weakref.ref[Quart]

    @property
    def func(self) -> t.Any:
        """Wrap the job's function in an async function that pushes a Quart
        application context. Sync functions are also supported, relying on
        Quart's ``ensure_async`` and asgiref.
        """
        func = t.cast(t.Callable[..., t.Any], super().func)
        app = self._quart_app()
        assert app is not None

        async def new_func(*args: t.Any, **kwargs: t.Any) -> t.Any:
            async with app.app_context():
                return await app.ensure_async(func)(*args, **kwargs)

        return update_wrapper(new_func, func)


def make_job_class(app: Flask | Quart) -> type[Job]:
    """Create the appropriate job class for the given app. The app is stored on
    the new subclass so that it can push an app context and wrap sync/async
    functions.

    :param app: The app to create a bound job class for.
    """
    cls: type[Job]

    if isinstance(app, Flask):
        cls = type("BoundFlaskJob", (FlaskJob,), {"_flask_app": weakref.ref(app)})
    else:
        cls = type("BoundQuartJob", (QuartJob,), {"_quart_app": weakref.ref(app)})

    return cls

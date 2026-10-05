from __future__ import annotations

import asyncio
import contextvars
import sys
import threading
import typing as t
from collections import abc as cabc
from typing import Any

from rq.job import Job


class FlaskJob(Job):
    def _execute(self) -> Any:
        """Run the job's function with its arguments.

        Handles coroutines better by cleaning up the loop and working when in an
        existing loop.
        """
        assert self.func is not None
        result = self.func(*self.args, **self.kwargs)

        if not asyncio.iscoroutine(result):
            return result

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No loop (Flask), run and clean up directly.
            return asyncio.run(result)

        # There is an existing async loop (Quart CLI pushing its app context).
        # Cannot schedule the coroutine on the existing loop. This sync function
        # would have to block waiting on the result and would never let the
        # coroutine start. Use a new thread with a new loop to set the result.

        if sys.version_info >= (3, 14):
            t = threading.Thread(
                target=self._loop_in_thread,
                args=(result,),
                context=contextvars.copy_context(),
            )
        else:
            t = threading.Thread(
                target=self._loop_in_thread,
                args=(result, contextvars.copy_context()),
            )

        t.start()
        t.join()
        return self._result

    def _loop_in_thread(
        self,
        coro: cabc.Coroutine[t.Any, None, None],
        context: contextvars.Context | None = None,
    ) -> None:
        if context is None:
            self._result = asyncio.run(coro)
        else:
            self._result = context.run(asyncio.run, coro)

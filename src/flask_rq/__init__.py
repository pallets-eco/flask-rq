from __future__ import annotations

import typing as t

from .extension import RQ
from .extension import job
from .extension import get_queue
from .extension import get_worker

__all__ = [
    "get_queue",
    "get_worker",
    "job",
    "RQ",
]


def __getattr__(name: str) -> t.Any:
    import importlib.metadata
    import warnings

    if name == "__version__":
        warnings.warn(
            "'__version__' is deprecated and will be removed in Flask-RQ 1.0."
            " Use 'importlib.metadata.version(\"flask-rq\")' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return importlib.metadata.version("flask-rq")

    raise AttributeError(name)

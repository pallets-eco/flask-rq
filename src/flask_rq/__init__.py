from __future__ import annotations

import typing as t

from ._extension import RQ

__all__ = [
    "RQ",
]


def __getattr__(name: str) -> t.Any:
    import warnings

    if name == "__version__":
        from importlib.metadata import version

        warnings.warn(
            "'__version__' is deprecated and will be removed in Flask-RQ 1.0."
            " Use 'importlib.metadata.version(\"flask-rq\")' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return version("flask-rq")

    if name in {"get_queue", "get_worker", "job"}:
        from . import _old

        warnings.warn(
            f"'{name}' is deprecated and will be removed in Flask-RQ 1.0. Use"
            " the corresponding 'RQExtension' method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(_old, name)

    raise AttributeError(name)  # pragma: no cover

from __future__ import annotations

import inspect

import pytest

from flask_rq import RQ


def mul(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def test_decorate_plain(rq: RQ) -> None:
    """Decorate without parentheses."""
    job_mul = rq.job(mul)
    assert job_mul.queue == "default"


def test_decorate_call(rq: RQ) -> None:
    """Decorate with parentheses, without argument."""
    job_mul = rq.job()(mul)
    assert job_mul.queue == "default"


def test_decorate_arg(rq: RQ) -> None:
    """Decorate with argument."""
    job_mul = rq.job(queue="low")(mul)
    assert job_mul.queue == "low"


def test_wrap_direct(rq: RQ) -> None:
    """Decorate with function and argument."""
    job_mul = rq.job(mul, queue="low")
    assert job_mul.queue == "low"


def test_callable(rq: RQ) -> None:
    """Wrapper is callable and acts like the wrapped function."""
    job_mul = rq.job(mul)
    assert callable(job_mul)
    assert job_mul(3, 4) == 12


def test_wrapped(rq: RQ) -> None:
    """Wrapper has wrapped function's attributes."""
    job_mul = rq.job(mul)
    assert job_mul.__doc__ == mul.__doc__
    assert inspect.unwrap(job_mul) == mul


@pytest.mark.usefixtures("app_ctx")
def test_job_default(rq: RQ) -> None:
    job_mul = rq.job(mul)
    j = job_mul.enqueue(6, 7)
    assert j.origin == "default"
    r = j.latest_result()
    assert r is not None
    assert r.return_value == 42


@pytest.mark.usefixtures("app_ctx")
def test_job_low(rq: RQ) -> None:
    job_mul = rq.job(queue="low")(mul)
    j = job_mul.enqueue(4, 8)
    assert j.origin == "low"
    r = j.latest_result()
    assert r is not None
    assert r.return_value == 32


@pytest.mark.usefixtures("app_ctx")
def test_deprecated_delay(rq: RQ) -> None:
    job_mul = rq.job(mul)

    with pytest.warns(DeprecationWarning, match="The 'delay' method"):
        job_mul.delay(4, 5)

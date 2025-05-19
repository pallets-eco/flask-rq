from __future__ import annotations

import typing as t

import click
import typing_extensions as te
from click.decorators import _param_memo  # pyright: ignore
from flask import Flask
from flask.cli import ScriptInfo as FlaskScriptInfo
from rq import cli as orig_cli

if t.TYPE_CHECKING:
    from quart import Quart
    from quart.cli import ScriptInfo as QuartScriptInfo

    from ._extension import RQ

P = te.ParamSpec("P")
R = t.TypeVar("R")


def make_cli(app: Flask | Quart) -> None:
    """Create the CLI group and commands, and register it with the app's CLI.

    This is needed because Flask and Quart define separate ``AppGroup`` classes,
    which applies the appropriate ``with_appcontext`` wrapper.

    :param app: The app to create the CLI for.
    """
    group = app.cli.group("rq")(rq_group)
    group.command("worker", with_appcontext=True)(worker_cmd)
    app.cli.add_command(group)


def from_rq_cmd(
    base_cmd: click.Command, names: set[str]
) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
    """Create a decorator that applies the named parameters from the original RQ
    CLI command to the new Flask-RQ CLI command.

    :param base_cmd: The original RQ CLI command.
    :param names: The parameter names to use.
    """

    def decorator(f: t.Callable[P, R]) -> t.Callable[P, R]:
        if not f.__doc__:
            f.__doc__ = base_cmd.help

        for param in reversed(base_cmd.params):
            if param.name in names:
                _param_memo(f, param)

        return f

    return decorator


@click.pass_context
def rq_group(ctx: click.Context) -> None:
    """Flask-RQ worker and queue commands."""
    script_info: FlaskScriptInfo | QuartScriptInfo = ctx.obj
    app = script_info.load_app()
    rq_ext: RQ = app.extensions["rq"]
    ctx.obj = rq_ext


@from_rq_cmd(
    orig_cli.worker,  # type: ignore[attr-defined]
    {
        "burst",
        "name",
        "results_ttl",
        "worker_ttl",
        "maintenance_interval",
        "job_monitoring_interval",
        "max_jobs",
        "max_idle_time",
        "with_scheduler",
        "queues",
    },
)
@click.pass_obj
def worker_cmd(
    obj: RQ,
    burst: bool,
    name: str | None,
    results_ttl: int,
    worker_ttl: int,
    maintenance_interval: int,
    job_monitoring_interval: int,
    max_jobs: int | None,
    max_idle_time: int | None,
    with_scheduler: bool,
    queues: list[str],
) -> None:
    worker = obj.make_worker(
        queues,
        name=name,
        default_result_ttl=results_ttl,
        worker_ttl=worker_ttl,
        maintenance_interval=maintenance_interval,
        job_monitoring_interval=job_monitoring_interval,
    )
    worker.work(
        burst=burst,
        max_jobs=max_jobs,
        max_idle_time=max_idle_time,
        with_scheduler=with_scheduler,
    )

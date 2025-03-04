from __future__ import annotations

import typing as t
from pkgutil import resolve_name

from flask import Flask
from quart import Quart
from rq import Queue

from flask_rq._job_class import make_job_class

if t.TYPE_CHECKING:
    from redis import Redis


def make_queues(app: Flask | Quart) -> dict[str, Queue]:
    config = app.config.get_namespace("RQ_")
    conn_confs: dict[str, dict[str, t.Any] | str | None] = config.get(
        "queue_connections", {}
    )
    conn_confs["default"] = config.get("connection", {})
    conn_cls_conf: str | type[Redis] = config.get("connection_class", "redis.Redis")

    if isinstance(conn_cls_conf, str):
        conn_cls: type[Redis] = resolve_name(conn_cls_conf)
    else:
        conn_cls = conn_cls_conf

    if (is_async := config.get("async", None)) is None:
        is_async = not app.testing

    connections: dict[str, Redis] = {}
    conn_refs: dict[str, str] = {}

    # Collect connections by name first. This allows using forward references to
    # use the same Redis connection/pool across queues. Each named queue can
    # either define a connection or a reference to another defined connection.
    for name, conn_conf in conn_confs.items():
        if conn_conf is None:
            continue

        if isinstance(conn_conf, str):
            if "://" not in conn_conf:
                # This is a forward reference to another connection.
                conn_refs[name] = conn_conf
            else:
                # This is a connection URL.
                connections[name] = conn_cls.from_url(conn_conf)  # pyright: ignore
        else:
            connections[name] = conn_cls(**conn_conf)

    default_conn = connections["default"]
    job_class = make_job_class(app)
    queues: dict[str, Queue] = {
        "default": Queue(
            "default", default_conn, is_async=is_async, job_class=job_class
        )
    }

    # All defined connections have been created, now create each queue with the
    # connection it references.
    for name in config.get("queues", []):
        if name == "default":
            continue

        if name in connections:
            conn = connections[name]
        elif name in conn_refs:
            if (conn_name := conn_refs[name]) in connections:
                conn = connections[conn_name]
            else:
                raise RuntimeError(
                    f'\'RQ_QUEUE_CONNECTIONS["{conn_name}"] must be defined'
                    f' for RQ_QUEUE_CONNECTIONS["{name}"] to reference it.\''
                )
        else:
            conn = default_conn

        queues[name] = Queue(name, conn, is_async=is_async, job_class=job_class)

    return queues

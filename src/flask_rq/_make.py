from __future__ import annotations

import typing as t
from pkgutil import resolve_name

from flask import Flask
from redis.connection import parse_url
from rq import Queue

from flask_rq._job_class import make_job_class

if t.TYPE_CHECKING:
    from quart import Quart
    from redis import Redis


def make_queues(app: Flask | Quart) -> dict[str, Queue]:
    config = app.config.get_namespace("RQ_")
    queue_names: list[str] = config.pop("queues", [])
    is_async: bool | None = config.pop("async", None)
    conn_confs: dict[str, dict[str, t.Any] | str | None] = config.pop(
        "queue_connections", {}
    )
    conn_cls_conf: str | type[Redis] = config.pop("connection_class", "redis.Redis")

    if "connection" in config:
        conn_confs["default"] = config.pop("connection")

    # After popping the supported keys, anything left is the old config format.
    if config:
        old_confs = handle_old_conf(config, conn_confs)

        if old_confs:
            conn_confs |= old_confs
            queue_names.extend(old_confs)

    if isinstance(conn_cls_conf, str):
        conn_cls: type[Redis] = resolve_name(conn_cls_conf)
    else:
        conn_cls = conn_cls_conf

    if is_async is None:
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

    if "default" in connections:
        default_conn = connections["default"]
    else:
        connections["default"] = default_conn = conn_cls()

    job_class = make_job_class(app)
    queues: dict[str, Queue] = {
        "default": Queue(
            "default", default_conn, is_async=is_async, job_class=job_class
        )
    }

    # All defined connections have been created, now create each queue with the
    # connection it references.
    for name in queue_names:
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


def handle_old_conf(
    config: dict[str, t.Any], conn_confs: dict[str, dict[str, t.Any] | str | None]
) -> dict[str, t.Any]:
    import warnings

    old_confs: dict[str, dict[str, t.Any]] = {}
    warn_keys: list[str] = []

    for key, value in config.items():
        name, sep, part = key.partition("_")

        if not sep or not part:
            # This is an unknown config key, ignore it.
            continue

        warn_keys.append(f"RQ_{key.upper()}")

        if name in conn_confs:
            # Prefer new config format.
            continue

        if part == "url":
            if "db" not in (parsed_value := parse_url(value)):  # type: ignore[no-untyped-call]
                if (db_key := f"{name}_db") in config:
                    parsed_value["db"] = config[db_key]

            old_confs[name] = parsed_value
        else:
            old_confs.setdefault(name, {})[part] = value

    if warn_keys:
        warn_keys_str = ", ".join(warn_keys)
        warnings.warn(
            "The config format has changed to use the 'RQ_QUEUES' dict"
            " instead of individual keys. The old format is deprecated and"
            " will not be used in Flask-RQ 1.0. Move the following keys to"
            f" the new format: {warn_keys_str}",
            DeprecationWarning,
            stacklevel=3,
        )

    return old_confs

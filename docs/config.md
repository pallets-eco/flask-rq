# Configuration

Configuration for Flask-RQ uses the following Flask config keys.

```{module} flask_rq.config
```

```{data} RQ_CONNECTION
:type: str | dict[str, typing.Any] | None
:value: "redis://127.0.0.1:6379/0"

The default Redis connection to use for each queue. The default assumes a local
server. This can be a URL string or a dict of arguments to pass to
{data}`RQ_CONNECTION_CLASS`.
```

```{data} RQ_QUEUES
:type: list[str] | None
:value: ["default"]

The names of the RQ queues to manage, in priority order. Each queue will use the
default connection {data}`RQ_CONNECTION` unless it is overrdden in
{data}`RQ_QUEUE_CONNECTIONS`.

By default, a single `"default"` queue is configured. If you pass a list of
names, you must include `"default"` if you want to access {attr}`.RQ.queue`.

.. versionchanged:: 1.0
    `"default"` is not added automatically if other names are listed.
```

```{data} RQ_ASYNC
:type: bool | None
:value: None

Controls RQ's {attr}`rq.Queue.is_async` setting for every queue. When
`is_async` is disabled, then `enqueue` immediately executes the job, rather than
needing a separate worker process. However, a Redis server is still needed to
handle RQ's various bookkeeping needs. If this is the default `None`, then
`is_async` is disabled if {attr}`app.testing <flask.Flask.testing>` is enabled.

See {doc}`testing` for more information.
```

```{data} RQ_QUEUE_CONNECTIONS
:type: dict[str, str | dict[str, typing.Any]]
:value: {}

Specifies queues that will use a different connection than
{data}`RQ_CONNECTION`. Each named queue must be listed in {data}`RQ_QUEUES`, and
`"default"` cannot be overridden. Each value can be a URL string, a string
naming another queue to use its connection, or a dict of arguments to pass to
{data}`RQ_CONNECTION_CLASS`.

See {doc}`queue` for more information.
```

```{data} RQ_CONNECTION_CLASS
:type: str | type[redis.Redis] | None
:value: "redis.Redis"

The class to use for each Redis connection. This can be a string to import or a
class.
```

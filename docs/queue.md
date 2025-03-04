# Queues

For many applications, using the single `"default"` queue will be all they ever
need. That said, RQ allows enqueuing jobs on different named queues. Workers can
be started watching specific queues, so for example you can start one worker
watching to the `"default"` queue, and three workers watching the `"priority"`
queue.

## Configuring Queues

By default, with no configuration, Flask-RQ uses the `"default"` queue and
connects to a local Redis server. This should be fine for most applications.

If you want to use more queues, you must name each one using the
{data}`.RQ_QUEUES` config. The `"default"` queue is always configured, regardless
of if it's listed.

```python
RQ_QUEUES = ["email", "priority"]
```

The above results in three queues (including `"default"`), all using the same
Redis connection pool. The connection is configured using the
{data}`.RQ_CONNECTION` config.

```python
RQ_CONNECTION = "redis://redis.my-app.example"
```

The above results in a connection to `redis.my-app.example` instead of `localhost`.

## Using Queues

To access the default queue, use {attr}`.RQ.queue`. Other named
queues are available through the {attr}`.RQ.queues` dict, for example
`rq.queues["email"]`.

Use the queue's `enqueue` method to add a job with arguments. The job will be
performed in the background by a worker.

```python
rq.queue.enqueue(update_stats, data=...)
rq.queues["email"].enqueue(send_passord_reset, user_id=user.id)
```

## The `job` Decorator

The {meth}`.RQ.job` decorator wraps a function to give it an
{meth}`enqueue <.JobWorker.enqueue>` method that automatically enqueues the
function using the extension instance and given queue name.

```python
@rq.job(queue="email")
def send_password_reset(user_id: int) -> None:
    ...

send_password_reset.enqueue(user_id=user.id)

# same as
rq.queues["email"].enqueue(send_password_reset, user_id=user.id)
```

The queue can be overridden, it only applies when using the added method. The
following uses the `"priority"` queue even though the job was configured for the
`"email"` queue.

```python
rq.queues["priority"].enqueue(send_password_reset, user_id=user.id)
```

## Other Connections

Queues can also use separate connections. By default, all queues use the same
connection, and this is typically all you'll need. However, you might have a
more complicated setup, such as having another RQ system elsewhere with its own
Redis server. In this case, you can define a queue that sends to that connection
instead. Note that a worker only listens on one connection, so you'd need to
start workers for each connection.

To change the connection for a queue, use the {data}`.RQ_QUEUE_CONNECTIONS`
config. This is a dict of queue name to connection settings. Queues that are not
listed in {data}`.RQ_QUEUES` are ignored. `None` values are ignored. A
`"default"` key is ignored, it's only configured with {data}`.RQ_CONNECTION`.

```python
RQ_QUEUE_CONNECTIONS = {"email": "redis://email-redis.my-app.example"}
```

Just as the queues share the same default Redis connection pool, you can
use references to share another connection between queues.

```python
RQ_CONNECTION = "redis://redis.my-app.example"
RQ_QUEUES = ["priority", "email", "email-priority"]
RQ_QUEUE_CONNECTIONS = {
    "email": "redis://email-redis.my-app.example",
    "email-priority": "email"
}
```

The above results in the `"default"` and `"priority"` queues sharing the default
connection, while the `"email-priority"` queue shares the same separate
connection as `"email"`.

# Getting Started

These docs cover setting up Flask-RQ, and the basics of using RQ. See the
[RQ docs] for more detailed information on using RQ itself.

[RQ docs]: https://python-rq.org

## Initialize the Application

First, set up your Flask/Quart application (or application factory) and the
{class}`.RQ` instance.

This extension follows the common pattern of Flask extension setup. Either
immediately pass an app to {class}`.RQ`, or call {meth}`~.RQ.init_app` later.

```python
from flask_rq import RQ

rq = RQ()
rq.init_app(app)  # call in the app factory if you're using that pattern
```

By default, the `"default"` queue is created and connects to
`redis://localhost:6379`. Connections and additional queues can be
configured, see {doc}`config`.

A Redis server must be available to enqueue jobs and start workers. See
{doc}`server` for more information.

## Run a Worker

At least one worker must be running to execute jobs. Flask-RQ provides a CLI
command to start a worker.

```
$ flask rq worker
```

See {doc}`worker` for more information.

## Execute a Job

Any Python callable, sync or `async`, can be an RQ job without any special
setup. The only requirement is that it is importable. Arguments can have any
pickleable data. However, it's best to keep it to simple data such as a user id
rather than an entire object, as it is much less data to store.

To execute a job, call a queue's `enqueue` method, passing the job function and
any positional and keyword arguments. {attr}`.RQ.queue` is the default queue, or
a queue can be accessed by name through the {attr}`.RQ.queues` dict.

```python
def send_password_reset(user_id: int) -> None:
    ...

# the default queue
rq.queue.enqueue(send_password_reset, user.id)

# a named queue
rq.queues["email"].enqueue(send_password_reset, user.id)
```

As a shortcut, decorate a function with the {meth}`.RQ.job` decorator. This
gives it an `enqueue` method that automatically uses the extension and given
queue.

```python
@rq.job(queue="email")
def send_password_reset(user_id: int) -> None:
    ...

send_password_reset.enqueue(user.id)
```

Flask-RQ does some special setup when creating the worker to ensure each job is
run in the Flask or Quart application's context. This means that accessing
`current_app`, databases, and other extensions will be available just like in
view functions and CLI commands.

See {doc}`job` and {doc}`queue` for more information.

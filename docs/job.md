# Jobs

RQ uses a very convenient API, where any Python function that is importable can
be submitted as a job without any special handling on your part. It already
supports sync `def` and `async def` functions.

Flask-RQ does some special setup when creating the worker to ensure each job is
run in the Flask or Quart application's context. This means that accessing
`current_app`, databases, and other extensions will be available just like in
view functions and CLI commands.

## Queuing a Job

Call a queue's `enqueue` method, passing a job function and any arguments. A
queue has other methods for scheduling, and some arguments can be give to
customize the job's information. See the [RQ docs] for more information.

[RQ docs]: https://python-rq.org/docs/

```python
def update_stats(data):
    ...

async def send_password_reset(user_id):
    ...

rq.queue.enqueue(update_stats, data=...)
rq.queues["email"].enqueue(send_passord_reset, user_id=user.id)
```

Both sync `def` and `async def` functions can be queued in the same way. Behind
the scenes, Flask-RQ will add the appropriate wrapper to activate the app
context, and the RQ worker will start an asyncio event loop if needed.

## The `job` Decorator

The {meth}`.RQ.job` decorator wraps a function to give it an
{meth}`enqueue <.JobWorker.enqueue>` method that automatically enqueues the
function using the extension instance and given queue name.

```python
@rq.job(queue="email")
async def send_password_reset(user_id: int) -> None:
    ...

send_password_reset.enqueue(user_id=user.id)

# same as
rq.queues["email"].enqueue(send_password_reset, user_id=user.id)
```

This added `enqueue` method retains the static type signature of the wrapped
function, meaning your type checker can check the call unlike the generic call
to `queue.enqueue`.

The wrapped function can still be called as a plain function as well.

```python
await send_password_reset(user_id=user.id)
```

## Async

Flask-RQ supports both Flask and Quart, and sync and async job functions. RQ
handles sync and async job functions, but only uses the `redis.Redis` sync
connection to communicate with Redis. You might be concerned that calling
`enqueue` from an `async def` view function is blocking, but in practice it
is a very fast operation to make some Redis API calls to record the job
information. You can use {meth}`asyncio.to_thread` to call `enqueue` if you find
that it is still an issue, or look into contributing async support to RQ.

```python
await asyncio.to_thread(rq.enqueue, send_password_reset, user_id=user.id)
```

## Scheduled Jobs

RQ queues have two more methods that will enqueue the job to run at a specified
time.

- `rq.queue.enqueue_at(datetime, func, ...)` - a worker will execute the
  function at the given {class}`~datetime.datetime`.
- `rq.queue.enqueue_in(timedelta, func, ...` - a worker will execute the
  function after the given {class}`~datetime.timedelta` interval has passed.

This requires running at least one worker with the scheduler enabled. Running
multiple workers with the scheduler is also ok.

```
$ flask rq worker --with-scheduler
```

RQ does not currently provide a way to run jobs on a repeated interval or Cron
schedule. [RQ-Scheduler][] provides separate commands for doing so, but Flask-RQ
does not yet provide integration, so any jobs will not be run in the app context
automatically.

[RQ-Scheduler]: https://github.com/rq/rq-scheduler

It is possible to schedule repeat intervals without RQ-Scheduler by
having a job enqueue itself again after running. You can use RQ's job callback
feature to ensure it's rescheduled or retired regardless of success.

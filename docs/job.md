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
queue has other methods, and some arguments can be given to customize the job's
information. See the [RQ docs] for more information.

[RQ docs]: https://python-rq.org/docs/

```python
def update_stats(data):
    ...

async def send_password_reset(user_id):
    ...

rq.queue.enqueue(update_stats, data=...)
rq.queues["email"].enqueue(send_passord_reset, user_id=user.id)
```

Both sync `def` and `async def` job functions are supported.

Jobs can be scheduled to run in the future or periodically. See {doc}`schedule`
for more information.

(job-decorator)=
## The `job` Decorator

The {meth}`.RQ.job` decorator wraps a function to give it enqueue methods that
use the extension instance and given queue name. See {class}`.JobWrapper` for
the available methods.

```python
@rq.job(queue="email")
async def send_password_reset(user_id: int) -> None:
    ...

send_password_reset.enqueue(user_id=user.id)

# same as
rq.queues["email"].enqueue(send_password_reset, user_id=user.id)
```

The added methods retain the static type signature of the wrapped function,
meaning your type checker can check the call, unlike the generic call to
`queue.enqueue`.

The wrapper can be called to execute the wrapped function directly.

```python
await send_password_reset(user_id=user.id)
```

:::{warning}
Due to the way RQ references jobs, it's not possible to pass decorated jobs to
`queue.enqueue` or other functions.

Either use the wrapper's methods, or pass its {attr}`~.JobWrapper.func`
attribute.

```python
send_reminder.cron_register("0 0 * * 1-5")

# same as
rq.cron.register(send_reminder.func, cron="0 0 * * 1-5")
```
:::

## Async

Flask-RQ supports both Flask and Quart. Sync `def` and `async def` functions can
be queued in the same way. Behind the scenes, Flask-RQ will add the appropriate
wrapper to activate the app context, and the RQ worker will start an asyncio
event loop if needed.

RQ only uses the `redis.Redis` sync connection to communicate with Redis. You
might be concerned that calling `enqueue` from an `async def` view function is
blocking, but in practice it is a very fast operation to record the job
information. You can use {meth}`asyncio.to_thread` to call `enqueue` if you find
that it is still an issue, or look into contributing async support to RQ.

```python
await asyncio.to_thread(rq.enqueue, send_password_reset, user_id=user.id)
```

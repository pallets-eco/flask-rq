# Scheduled Jobs

RQ provides two ways to schedule jobs to run in the future and perodically.
Unfortunately, they both use the name "scheduler", but accomplish different
goals. Both may run at the same time.

The basic scheduler runs as part of the worker. It allows enqueued jobs to wait
to run until a specified time. It can repeat jobs a specified finite number of
times.

The cron scheduler runs as a separate process. It enqueues jobs based
on configured intervals or schedules. The jobs will repeat periodically until
the scheduler is stopped.

## Future Jobs

A queue's `enqueue` method runs the job as soon as possible. Two other
methods are provided to tell workers to wait until a specified time
before taking the job.

- `rq.queue.enqueue_at(datetime, func, ...)` - A worker will wait until the
  given {class}`~datetime.datetime` to take the job.
- `rq.queue.enqueue_in(timedelta, func, ...` - A worker will wait until the
  given {class}`~datetime.timedelta` interval has passed to take the job.

See the [RQ docs on scheduling](https://python-rq.org/docs/scheduling/) for more
information.

This requires running at least one worker with the scheduler enabled. Running
multiple workers with the scheduler is also ok.

```
$ flask rq worker --with-scheduler
```

This still requires enqueuing the job from your code. It cannot independently
enqueue jobs on a schedule. That's what the Cron scheduler is for.

It is possible to schedule continuous intervals without the Cron scheduler by
having a job enqueue itself again after running. You can use RQ's job callback
feature to ensure it's rescheduled or retried regardless of success.

### The `job` Decorator

The {meth}`~.RQ.job` decorator provides {meth}`~.JobWrapper.enqueue_at` and
{meth}`~.JobWrapper.enqueue_in` methods as well. As an extra convenience,
`enqueue_in` accepts an `int` of seconds or a `timedelta`.

```python
delete_temporary_files.enqueue_in(30)
```

## Cron Scheduled Jobs

The Cron scheduler continuously schedules jobs at fixed intervals.

The schedule is defined ahead of time and the scheduler runs as a separate
process periodically enqueuing jobs according to the schedule. To run the
scheduler:

```
$ flask rq cron
```

Jobs can be scheduled globally with the {func}`rq.cron.register` method. Or
they can be registered specific to the extension instance with
{meth}`.RQ.cron_register`. Flask-RQ adds both the global and instance jobs when
running the scheduler.

RQ's global `register` method takes an `interval` number of seconds between job
runs, or a `cron` string as interpreted by [croniter] to specify more complex
intervals. For convenience, the extension's `cron_register` method uses the
second positional argument for both `interval` and `cron`, and uses the
`"default"` queue by default.

[croniter]: https://github.com/pallets-eco/croniter

See the [RQ docs on Cron](https://python-rq.org/docs/cron/) for more
information.

```python
# global registration, interval seconds
from rq import cron
cron.register(update_data_source, "default", interval=28_800)

# app-specific registration, cron string
rq = RQ(app)
rq.cron_register(delete_temporary_files, "0 2 * * *")
```

### The `job` Decorator

The {meth}`~.RQ.job` decorator provides a {meth}`~.JobWrapper.cron_register`
method as well. As an extra convenience, it uses the first positional argument
for both `interval` and `cron`.

```python
update_data_source.cron_register(28_800)
delete_temporary_files.cron_register("0 2 * * *")
```

### Legacy RQ-Scheduler Library

Before it was implemented in RQ, Cron support was previously provided by a
separate [RQ-Scheduler] library. Flask-RQ does not provide integration with
this, so it will need to be configured manually, and any jobs will not be run in
the app context. Prefer using RQ's built-in Cron support.

[RQ-Scheduler]: https://github.com/rq/rq-scheduler

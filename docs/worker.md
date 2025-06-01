# Workers

Workers are separate processes that watch the RQ queues and execute jobs as they
are enqueued. At least one worker is required. If no workers are running, you
won't get any errors when enqueuing jobs, but the jobs will never run.

Flask-RQ does some special setup when creating the worker to ensure each job is
run in an application context. This means that accessing `current_app`,
databases, and other extensions will be available just like in view functions
and CLI commands.

See the [RQ docs] for more information on workers.

[RQ docs]: https://python-rq.org/

## Starting a Worker

You _must_ use Flask-RQ to start the worker if you want jobs to run inside the
app context. There are two ways to do so. You can start more workers by running
the command multiple times in separate processes.

### CLI Command

The most straightforward is the `flask rq worker` CLI command.

```
$ flask rq worker
```

This takes many, but not all, of the options that RQ's own `rq worker` command
does, but goes through Flask-RQ to create the job class and worker. Pass the
`--help` to see what options are available.

### Worker Script

If you need to customize the worker beyond what the CLI enables, you can write a
Python script to create and run the worker. The script must import your app and
the extension, create an app context, and then call {meth}`.RQ.make_worker`.
You can pass whatever arguments you need to `make_worker` and the worker's
`work` method, and do any other customizations you need during the script.

```python
# my_worker.py
from my_app import create_app, rq

app = create_app()

with app.app_context():
    worker = rq.make_worker()
    worker.work()
```

```
$ python my_worker.py
```

## Queues and the Connection

By default, the worker will watch all configured queues ({data}`RQ_QUEUES`) in
the order configured. You can pass a list of queues to the CLI
command or {meth}`RQ.make_worker`, in which case the worker will only watch
those queues. Either way, the first listed queue's connection is used.

```
# all queues, first configured queue's connection
$ flask rq worker

# two queues, email's connection
$ flask rq worker email email-priority
```

## RQ's CLI

RQ provides its own `rq` CLI. As stated above, you must use the
`flask rq worker` command to start the workers. All the other `rq` commands can
be used directly, although they will require some manual configuration since
they don't know about your Flask app configuration.

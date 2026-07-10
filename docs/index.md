# Flask-RQ

Flask-RQ is a [Flask]/[Quart] extension that background job execution using
[RQ].

RQ allows queueing functions to be run in separate worker processes,
allowing long-running jobs to run in the background without blocking the web app
from returning a response quickly. RQ also provides Cron support for scheduling
periodic jobs.

Flask-RQ allows configuring RQ using Flask's config, and handles executing jobs
in the application context, so other services like database connections are
available.

[Flask]: https://flask.palletsprojects.com
[Quart]: https://quart.palletsprojects.com
[RQ]: https://python-rq.org

## Install

Install from [PyPI]:

```text
$ pip install flask-rq
```

[PyPI]: https://pypi.org/project/flask-rq

## Source

The project is hosted on GitHub: <https://github.com/pallets-eco/flask-rq>.

```{toctree}
:hidden:

start
config
queue
job
schedule
worker
server
testing
api
license
changes
```

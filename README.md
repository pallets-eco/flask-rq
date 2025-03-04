# Flask-RQ

Flask-RQ is a [Flask]/[Quart] extension that background job execution using
[RQ]. RQ allows queueing functions to be run in separate worker processes,
allowing long-running jobs to run in the background without blocking the web app
from returning a response quickly. Flask-RQ allows configuring RQ using Flask's
config, and handles executing jobs in the application context, so other services
like database connections are available.

[Flask]: https://flask.palletsprojects.com
[Quart]: https://quart.palletsprojects.com
[RQ]: https://python-rq.org

## Pallets Community Ecosystem

> [!IMPORTANT]\
> This project is part of the Pallets Community Ecosystem. Pallets is the open
> source organization that maintains Flask; Pallets-Eco enables community
> maintenance of related projects. If you are interested in helping maintain
> this project, please reach out on [the Pallets Discord server][discord].

[discord]: https://discord.gg/pallets

## Installation

Install from [PyPI]:

```
$ pip install flask-rq
```

[PyPI]: https://pypi.org/project/Flask-RQ/

## Example

```python
from flask import Flask, g
from flask_rq import RQ

app = Flask(__name__)
rq = RQ(app)

@rq.job
def send_password_reset_job(user_id:  int) -> None:
    ...

@app.route("/auth/send-password-reset")
def send_password_reset():
    send_password_reset_job.enqueue(user_id=g.user.id)
    return "Check your email!"
```

```
$ flask rq worker
```

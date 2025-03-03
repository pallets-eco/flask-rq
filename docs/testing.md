# Testing

RQ queues can be set to execute jobs immediately in the local process when
enqueued, rather than requiring a separate worker process. When `app.testing`
is `True`, Flask-RQ will enable this mode automatically. It can also be forced
on or off using the {data}`RQ_ASYNC` config. A Redis server must still be
running in order for RQ to do its bookkeeping.

## Managing a Test Server

The best way to test is to run a local RQ server for the duration of the test
session. This ensures your code runs against a real server using the real
client connections, just as it will in production.

With Pytest, use a `session` scoped fixture to start `redis-server` in a
subprocess, and terminate it after all tests have run. Use a function scoped
fixture to clear all data after each test. Use [ephemeral-port-reserve] to pick
out a free port for the server.

[ephemeral-port-reserve]: https://pypi.org/project/ephemeral-port-reserve/

```python
import collections.abc as cabc
import subprocess
import time

import ephemeral_port_reserve
import pytest
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

@pytest.fixture(scope="session")
def redis_port() -> int:
    return ephemeral_port_reserve.reserve()  # type: ignore[no-any-return]


@pytest.fixture(scope="session", autouse=True)
def _start_redis(
    tmp_path_factory: pytest.TempPathFactory, redis_port: int
) -> cabc.Iterator[None]:
    proc = subprocess.Popen(
        ["redis-server", "--port", str(redis_port)],
        cwd=tmp_path_factory.mktemp("redis-server"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    while True:
        try:
            redis = Redis(port=redis_port, single_connection_client=True)
            redis.ping()
            break
        except (ConnectionError, RedisConnectionError):  # pragma: no cover
            time.sleep(0.1)

    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(autouse=True)
def _reset_redis(redis_port: int) -> cabc.Iterator[None]:
    yield
    Redis(port=redis_port, single_connection_client=True).flushall()

```

## CI and GitHub Actions

When running in CI, you'll need to get Redis installed. For GitHub Actions, you
can use the [shogo82148/actions-setup-redis][setup-redis] action to ensure Redis
is installed. Since your tests will start the server, tell the action not to
start it.

```yaml
steps:
  # ...
  - uses: shogo82148/actions-setup-redis@v1
    with:
      auto-start: false
  # ...
```

[setup-redis]: https://github.com/shogo82148/actions-setup-redis

## FakeRedis Library

Instead of requiring Redis to be installed and running a real server, you can
use the connection class provided by the [FakeRedis] library. This provides the
same API as the Python Redis library, but stores all the data in the local
Python memory. During testing, change {data}`RQ_CONNECTION_CLASS`.

```python
app.config["RQ_CONNECTION_CLASS"] = "fakeredis.FakeRedis"
```

[FakeRedis]: https://fakeredis.readthedocs.io

With Flask-RQ itself, a few tests failed for unclear reasons when using
FakeRedis. Your application may not run into issues.

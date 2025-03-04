# Redis Server

A Redis (or compatible alternative) server must be running in order to enqueue
jobs and start workers.

## Alternative Servers

[Redis] changed to a "source available" license in March 2024. A few forks were
created to continue with different licenses. Notably [Valkey] with a
BSD-3-Clause license, and [Redict] with an LGPL-3.0-only license. From limited
testing, RQ appears to work with either.

[Redis]: https://redis.io
[Valkey]: https://valkey.io
[Redict]: https://redict.io

## Running Locally

[Install Redis locally][Redis] and run `redis-server`. You can also run Valkey
with `valkey-server`, or Redict with `redict-server`.

## Docker

You can start a local server through Docker or Podman:

```
# Redis
$ docker run -d --rm -p 6379:6379 redis:latest

# Valkey
$ docker run -d --rm -p 6379:6379 valkey/valkey:latest

# Redict
$ docker run -d --rm -p 6379:6379 registry.redict.io/redict:latest
```

If you want data persisted across restarts, use a volume and tell the server to
save its data.

```
$ docker run -d --rm -p 6379:6379 --volume redis:/data \
    redis:latest redis-server --appendonly yes
```

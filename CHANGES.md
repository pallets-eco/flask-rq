## Version 1.0.0

Unreleased

- Remove previously deprecated code. Use 0.3 as an intermediate upgrade to see
  deprecation warnings.
    - The global API (`get_queue`, `get_worker`, `@job`) is removed.
    - The "flat" config is not used.
    - The `@job` decorator `delay` function is renamed to `enqueue`.
    - `__version__` is removed.
- The `"default"` queue is not configured automatically if `RQ_QUEUES` is set,
  it must be listed in that case. {issue}`53`
- The worker uses the order in `RQ_QUEUES` rather than putting `"default"`
  first. The first queue's connection is used, rather than the default's.
  {issue}`53`

## Version 0.3.3

Released 2025-06-01

- Compatibility with RQ 2.3.3. {issue}`51`

## Version 0.3.2

Released 2025-03-14

- Remove non-optional `quart` import.

## Version 0.3.1

Released 2025-03-04

- Fix error when `RQ_CONNECTION` is a URL string instead of a dict.

## Version 0.3.0

Released 2025-03-04

- Drop support for Python < 3.9.
- Require Flask >= 3.0.
- Require RQ >= 2.0.
- Modernize project tools and config.
- Full static type annotations.
- Move to a class-based extension API. The previously documented global API
  (`get_queue`, `get_worker`, `@job`) is deprecated. Use the corresponding
  methods on the extension instance instead.
- Add a `flask rq worker` command.
- Queue configuration is expanded. The `RQ_CONNECTION` config defines the
  default connection, and the `RQ_QUEUES` config defines the named queues.
  `RQ_QUEUE_CONNECTIONS` config can define non-default connections for queues.
  `RQ_CONNECTION_CLASS` config can change the `redis.Redis` class used. The
  previous "flat" config is deprecated.
- Added the `RQ_ASYNC` config key. By default, jobs are executed by workers. If
  this is enabled, or `app.testing` is enabled, jobs are executed directly.
- Redis connections and RQ queues are only created once rather than on each
  access. Connections can be shared between queues.
- Support Quart.
- Job functions are executed with the Flask/Quart application context active.
  This works for both Flask and Quart, for both sync `def` and `async def`
  functions.
- The `@job` decorator `delay` function is renamed to `enqueue` to match RQ,
  and the old name is deprecated.
- The extension instance is recorded in `app.extensions["rq"]`.
- `__version__` is deprecated. Use `importlib.metadata.version("flask-rq")`
  instead.

## Version 0.2.0

Released 2012-11-12

- Improve and simplify extension.
- Renamed `task` to `job`.

## Version 0.1.0

Released 2012-07-19

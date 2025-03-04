# Deprecated 0.2 API

Flask-RQ 0.2, released in 2012, provided a much lighter API, only the barest
wrapper around RQ to use Flask's config. In 2024, Flask-RQ was adopted by the
Pallets-Eco organization, and was entirely rewritten. Flask-RQ 0.3 retains
compatibility as best it can with the old API, as an intermediate step for
upgrading to 1.0.

```{deprecated} 0.3
The old API is deprecated and will be removed in Flask-RQ 1.0.
```

## API

```{eval-rst}
.. currentmodule:: flask_rq
.. autofunction:: job
.. autofunction:: get_queue
.. autofunction:: get_worker
```

## Configuration

Configuration keys use the form `RQ_{queue}_{arg}`. For example, `RQ_LOW_DB`
will configure the `db` connection argument for the queue named `"low"`.
`RQ_{queue}_URL` can be used to configure a connection by URL rather than args,
like `redis://localhost:6379/2`. The `"default"` queue always exists, and
connects to a local Redis server with its default port if not otherwise
configured. If a queue is not otherwise configured, it uses the default's
connection.

```python
app.config |= {
    "RQ_DEFAULT_HOST": "dev.example",
    "RQ_LOW_HOST": "dev.example",
    "RQ_LOW_DB": "1",
    "RQ_HIGH_URL": "redis://dev.example:6379/2",
}
```

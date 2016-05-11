Flask-RQ
========

.. image:: https://travis-ci.org/mattupstate/flask-rq.svg?branch=master
    :target: https://travis-ci.org/mattupstate/flask-rq

RQ (Redis Queue) integration for Flask applications


Resources
---------

- `Documentation <http://packages.python.org/Flask-RQ/>`_
- `Issue Tracker <http://github.com/mattupstate/flask-rq/issues>`_
- `Code <http://github.com/mattupstate/flask-rq/>`_
- `Development Version
  <http://github.com/mattupstate/flask-rq/zipball/develop#egg=Flask-RQ-dev>`_


Installation
------------

.. code-block:: bash

    $ pip install flask-rq


Getting started
---------------

To quickly start using `rq`, simply create an RQ instance:

.. code-block:: python

    from flask import Flask
    from flask.ext.rq import RQ


    app = Flask(__name__)
    rq = RQ()
    rq.init_app(app)

    default_queue = rq.create_queue() # Creates queue "default"

    # Us RQ's `enqueue` method
    rq.enqueue(some_function, queue_name='default')
    # Or use the Queue object returned from `create_queue`


``create_worker`` function
~~~~~~~~~~~~~~~~~~~~~~~

Returns a worker for default queue or specific queues for names given as arguments:

.. code-block:: python

    from flask.ext.rq import RQ

    app = Flask(__name__)
    rq = RQ()
    rq.init_app(app)

    # Using the default queue
    rq.create_queue()
    worker = rq.create_worker()
    worker.work()

    # Using a specific queue
    rq.create_queue('email')
    rq.create_queue('default')
    email_worker = rq.create_worker(queues=['email'])
    email_worker.work()
    # Note: These queues have to share the same connection


Configuration
-------------

By default Flask-RQ will connect to the default, locally running
Redis server. One can change the connection settings for the default
server like so:

.. code-block:: python

    app.config['RQ_DEFAULT_HOST'] = 'somewhere.com'
    app.config['RQ_DEFAULT_PORT'] = 6479
    app.config['RQ_DEFAULT_PASSWORD'] = 'password'
    app.config['RQ_DEFAULT_DB'] = 1

Queue connection can also be set using a DSN:

.. code-block:: python

    app.config['RQ_LOW_URL'] = 'redis://localhost:6379/2'


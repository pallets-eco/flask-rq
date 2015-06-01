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

    RQ(app)


``@job`` decorator
~~~~~~~~~~~~~~~~~~~

Provides a way to quickly set a function as an ``rq`` job:

.. code-block:: python

    from flask.ext.rq import job


    @job
    def process(i):
        #  Long stuff to process


    process.delay(3)


A specific queue name can also be passed as argument:

.. code-block:: python

    @job('low')
    def process(i):
        #  Long stuff to process


    process.delay(2)


``get_queue`` function
~~~~~~~~~~~~~~~~~~~~~~

Returns default queue or specific queue for name given as argument:

.. code-block:: python

    from flask.ext.rq import get_queue


    job = get_queue().enqueue(stuff)  # Creates a job on ``default`` queue
    job = get_queue('low').enqueue(stuff)  # Creates a job on ``low`` queue


``get_worker`` function
~~~~~~~~~~~~~~~~~~~~~~~

Returns a worker for default queue or specific queues for names given as arguments:

.. code-block:: python

    from flask.ext.rq import get_worker


    # Creates a worker that handle jobs in ``default`` queue.
    get_worker().work(True)
    # Creates a worker that handle jobs in both ``default`` and ``low`` queues.
    get_worker('default', 'low').work(True)
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


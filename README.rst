Flask-RQ
========

RQ (Redis Queue) integration for Flask applications


Resources
---------

- `Documentation <http://packages.python.org/Flask-RQ/>`_
- `Issue Tracker <http://github.com/mattupstate/flask-rq/issues>`_
- `Code <http://github.com/mattupstate/flask-rq/>`_
- `Development Version
  <http://github.com/mattupstate/flask-rq/zipball/develop#egg=Flask-RQ-dev>`_


.. image:: https://secure.travis-ci.org/Birdback/flask-rq.png


Contents
--------

* :ref:`installation`
* :ref:`getting-started`
* :ref:`configuration`


.. _installation:

Installation
------------

.. code-block:: bash

    $ pip install flask-rq


.. _getting-started:

Getting started
---------------

To quicly start using `rq`, simply create an RQ instance:

.. code-block:: python

    from flask import Flask
    form flask.ext.rq import RQ


    app = Flask(__name__)

    RQ(app)


``@task`` decorator
~~~~~~~~~~~~~~~~~~~

Provides a way to quickly set a function as an ``rq`` task:

.. code-block:: python

    from flask.ext.rq import task


    @task
    def process(i):
        #  Long stuff to process


A specific queue name can also be passed as argument:

.. code-block:: python

    @task('low')
    def process(i):
        #  Long stuff to process


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

    get_worker.work(True)  # Creates a worker that handle jobs in ``default`` queue.
    get_worker.work(['default', 'low'])  # Creates a worker that handle jobs in both ``default`` and ``low`` queues.


.. _configuration:

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


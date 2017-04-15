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

Sometimes you need to access application configuration context in your job. 
There is special way to be able to work inside of context. Please note this is 
not the same context. This is new, specially created context with the same 
configuration, but without blueprints or extensions that you probably expect.
For example after long task you want to send email with result report:

.. code-block:: python

    @job()
    def context_process():

        #  Long stuff to process

        from flask import current_app
        from flask.ext.mail import Mail, Message
        mail = Mail()
        # current_app.config is almost the same as in Flask application
        # that call your code 
        mail.init_app(current_app)  
        msg = Message("Report",
                  sender="from@example.com",
                  recipients=["to@example.com"])
        mail.send(msg)


    # inside of your view

    @app.route('/make_long_report')
    def report(project_id):
        context_process.ctx_delay()
        return 'Check your inbox in few minutes!'


If you need to differentiate contexts then name of Flask application inside of 
worker job is `worker`.


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


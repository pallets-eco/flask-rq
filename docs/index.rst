.. include:: ../README.rst


Contents
========
* :ref:`installation`
* :ref:`getting-started`
* :ref:`configuration`


.. _installation:

Installation
============

    $ pip install flask-rq


.. _getting-started:

Getting Started
===============

To quickly start processing jobs, create an instance of the RQ extension::

    import time
    from flask import Flask
    from flask_rq import RQ

    app = Flask(__name__)

    rq = RQ(app)

    @rq.task
    def long_process(echo):
        time.sleep(5)
        return echo

    @app.route('/')
    @app.route('/<word>')
    def echo(word=None):
        long_process(word)
        return 'Task queued: ' + word

To send a job to a particular queue, use the `name` argument::

    @rq.task('low')
    def long_process(echo):
        time.sleep(5)
        return echo

To send a job to a particular connection, use the `connection` argument::

    @rq.task('low', connection='default')
    def long_process(echo):
        time.sleep(5)
        return echo


.. _configuration:

Configuration
=============

Be default Flask-RQ will connect to the default, locally running
Redis server. One can change the connection settings for the default
server like so::

    app.config['RQ_DEFAULT_HOST'] = 'somewhere.com'
    app.config['RQ_DEFAULT_PORT'] = 6479
    app.config['RQ_DEFAULT_PASSWORD'] = 'password'
    app.config['RQ_DEFAULT_DB'] = 1

One can add additional server connection parameters. For example, the 
following code illustrates how to add a second set of Redis connection
values into the configuration and how to send jobs to it::
    
    from flask import Flask
    from flask_rq import RQ

    app = Flask(__name__)
    
    app.config['RQ_OTHER_HOST'] = 'myredisserver.com'
    app.config['RQ_OTHER_PORT'] = 6379
    app.config['RQ_OTHER_PASSWORD'] = 'secret'
    app.config['RQ_OTHER_DB'] = 0

    rq = RQ(app)

    @rq.task(connection='other')
    def long_process(echo):
        time.sleep(5)
        return echo

    @app.route('/')
    @app.route('/<word>')
    def echo(word=None):
        long_process(word)
        return 'Task queued: ' + word

Notice the keywork arguement named `connection` in the previous code.
This specifies that the job be sent to the connection specified in the
application configuration.

If you're function to be queued has conflicting keyword arguments you
can use the lower level api::

    @app.route('/')
    @app.route('/<word>')
    def echo(word=None):
        with rq.get_connection('other'):
            q = rq.get_queue('high')
            q.enqueue(log_process, word)
        return 'Task queued: ' + word


Changelog
=========

.. toctree::
   :maxdepth: 2

   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
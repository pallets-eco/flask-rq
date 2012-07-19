"""
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
"""

from setuptools import setup

setup(
    name='Flask-RQ',
    version='0.1',
    url='http://packages.python.org/Flask-RQ/',
    license='MIT',
    author='Matthew Wright',
    author_email='matt@nobien.net',
    description='RQ (Redis Queue) integration for Flask applications',
    long_description=__doc__,
    py_modules=['flask_rq'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask', 'rq'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

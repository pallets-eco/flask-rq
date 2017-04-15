# -*- coding: utf-8 -*-
import time
from flask_rq import job


@job
def simple(i):
    time.sleep(5)
    return i


@job('low')
def specified(i):
    time.sleep(5)
    return i

@job
def simple_ctx():
    from flask import current_app
    time.sleep(5)
    return current_app.name

# -*- coding: utf-8 -*-
import time
from flask_rq import task


@task
def simple(i):
    time.sleep(5)
    return i


@task('low')
def specified(i):
    time.sleep(5)
    return i

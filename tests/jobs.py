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

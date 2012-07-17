import os
import sys
sys.path.pop(0)
sys.path.insert(0, os.getcwd())

import time

from flask import Flask
from flask_rq import RQ

app = Flask(__name__)

app.config['RQ_OTHER_HOST'] = 'localhost'
app.config['RQ_OTHER_PORT'] = 6789
app.config['RQ_OTHER_PASSWORD'] = None
app.config['RQ_OTHER_DB'] = 0

rq = RQ(app)


def takes_a_while(echo):
    time.sleep(1)
    return echo


@app.route('/')
def home():
    return "Home"


@app.route('/doit')
def doit():
    rq.enque(takes_a_while, 'Hello World')


@app.route('/doit2')
def doit2():
    rq.enque(takes_a_while, 'Hello World',
             name="low", connection="other")

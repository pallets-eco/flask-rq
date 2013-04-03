
import time

from flask import Flask
from flask_rq import RQ

app = Flask(__name__)
app.debug = True

app.config['RQ_OTHER_HOST'] = 'localhost'
app.config['RQ_OTHER_PORT'] = 6379
app.config['RQ_OTHER_PASSWORD'] = None
app.config['RQ_OTHER_DB'] = 0

rq = RQ(app)

def takes_a_while(echo):
    time.sleep(1)
    return echo

@rq.job
def do_something(echo):
    time.sleep(1)
    return echo

@rq.job('low')
def do_something_low(echo):
    time.sleep(1)
    return echo

@rq.job('low', connection='other')
def do_something_low_on_connection(echo):
    time.sleep(1)
    return echo

@app.route('/')
def home():
    return "Home"

@app.route('/doit')
def doit():
    rq.enqueue(takes_a_while, 'do it')
    return 'Success'

@app.route('/doit2')
def doit2():
    rq.enqueue(takes_a_while, 'do it 2',
               name="low", connection="other")
    return 'Success'

@app.route('/doit3')
def doit3():
    with rq.get_connection():
        q = rq.get_queue('low')
        q.enqueue(takes_a_while, 'do it 3')
    return 'Success'

@app.route('/doit4')
def doit4():
    do_something('decorated')
    return 'Success'

@app.route('/doit5')
def doit5():
    do_something_low('doit5')
    return 'Success'

@app.route('/doit6')
def doit6():
    do_something_low_on_connection('doit6')
    return 'Success'

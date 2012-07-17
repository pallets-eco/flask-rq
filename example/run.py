import os
import sys
sys.path.pop(0)
sys.path.insert(0, os.getcwd())

from example.app import app

if __name__ == '__main__':
    app.run()

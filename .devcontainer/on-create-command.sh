#!/bin/bash
printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d
sudo apt-get update && sudo apt-get install -y redis-server
set -e
python3 -m venv --upgrade-deps .venv
. .venv/bin/activate
pip install -r requirements/dev.txt
pip install -e .

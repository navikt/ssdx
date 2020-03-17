#!/bin/bash

cd -- "$(dirname "$BASH_SOURCE")"
tput reset

echo "Starting ..."
cd .ssdx
git pull > /dev/null
cd ..
source .ssdx/venv/bin/activate
pip install -r .ssdx/python/requirements.txt > /dev/null
python .ssdx/python/run.py

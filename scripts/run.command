#!/bin/bash

cd -- "$(dirname "$BASH_SOURCE")"
tput reset

cd .ssdx
git pull
cd ..
source .ssdx/venv/bin/activate > /dev/null 
pip install -r .ssdx/python/requirements.txt > /dev/null 
python .ssdx/python/run.py

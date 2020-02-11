#!/bin/bash

cd -- "$(dirname "$BASH_SOURCE")"
tput reset

cd .ssdx
git pull
cd ..
source .ssdx/venv/bin/activate
python .ssdx/python/run.py
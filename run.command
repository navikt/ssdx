#!/bin/bash

cd -- "$(dirname "$BASH_SOURCE")"
tput reset

source .ssdx/venv/bin/activate
python .ssdx/scripts/run.py
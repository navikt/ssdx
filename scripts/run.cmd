:: init
@echo off
call cls

cd .ssdx
call git pull
cd ..
call .ssdx\venv\Scripts\activate
call pip install .ssdx\python\requirements.txt
call python .ssdx\python\run.py
:: init
@echo off
call cls

cd .ssdx
call git pull >nul 2>&1
cd ..
call .ssdx\venv\Scripts\activate
call pip install -r .ssdx\python\requirements.txt >nul 2>&1
call python .ssdx\python\run.py

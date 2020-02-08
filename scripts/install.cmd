@echo off

RD /S /Q "%cd%\.ssdx"
call git clone https://github.com/navikt/ssdx.git .ssdx
cd .ssdx

:: Check for Python Installation
python --version 3>NUL
if errorlevel 1 goto errorNoPython

:: Reaching here means Python is installed.
call pip3 install virtualenv
RD /S /Q "%cd%\venv"
call mkdir venv
call virtualenv venv
call venv\Scripts\activate
call pip install -r python\requirements.txt

echo f | xcopy /s /f "%cd%\scripts\run.cmd" "%cd%\..\run.cmd"

echo.
echo.
echo.
echo Finished!

echo.
echo Double click 'run.command' from you DX project root folder to run script.

set /p tmp="Press enter to open now or close window to exit installation."

cd ..
run.cmd

:: Once done, exit the batch file -- skips executing the errorNoPython section
goto:eof

:errorNoPython

call start https://www.python.org/ftp/python/3.8.0/python-3.8.0.exe
echo.
set /p tmp="Press enter after installing Python (REMEMBER TO CHECK 'ADD PYTHON 3.8 TO PATH')"

call start https://bootstrap.pypa.io/get-pip.py

echo.
echo Save get-pip.py to the root folder (%cd%)
set /p tmp="Press enter after saving at root"
call python get-pip.py
del get-pip.py
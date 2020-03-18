@echo off

RD /S /Q "%cd%\.ssdx"
call git clone https://github.com/navikt/ssdx.git .ssdx
cd .ssdx

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
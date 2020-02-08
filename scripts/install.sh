#!/bin/bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" </dev/null
brew install git

rm -rf .ssdx											# old install of ssdx
git clone https://github.com/navikt/ssdx.git .ssdx		# download app
cd .ssdx

brew install python3
pip3 install virtualenv
rm -rf venv
mkdir venv
virtualenv venv
source venv/bin/activate
pip install -r python/requirements.txt

cp scripts/run.command ../
chmod u+x ../run.command

echo "\n\n\nFinished!"

echo "\nDouble click 'run.command' from you DX project root folder to run script. Press enter to open now or close window to exit installation."
read varname

cd ..
sh run.command
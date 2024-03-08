#!/bin/bash

cd /usr/local/bin
git clone https://github.com/s-liwka/gato.git
cd gato
python -m venv .venv
source ".venv/bin/activate"
pip install -r requirements.txt
cp scripts/gato-cli.sh /usr/local/bin/gato-cli
cp scripts/gato-gui.sh /usr/local/bin/gato-gui
cp scripts/gato-update.sh /usr/local/bin/gato-update
chmod +x /usr/local/bin/gato-update
chmod +x /usr/local/bin/gato-gui
chmod +x /usr/local/bin/gato-cli
echo "INSTALL LIBVIPS BEFORE RUNNING!!"
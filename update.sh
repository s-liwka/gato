#!/bin/bash
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
echo "Update completed successfully."
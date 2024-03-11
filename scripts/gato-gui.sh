#!/bin/bash
source /usr/local/bin/gato/.venv/bin/activate
cd /usr/local/bin/gato
python /usr/local/bin/gato/main.py "$@"

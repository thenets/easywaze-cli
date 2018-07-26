#!/bin/bash


cd /app

source $USER_HOME/.pyenv/versions/venv/bin/activate
pip install -r /app/requirements.txt


cd ..
export PYTHONPATH=.
python app/exporters/export.py to_postgis
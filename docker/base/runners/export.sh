#!/bin/bash

# Enable virtualenv
. $USER_HOME/.pyenv/versions/venv/bin/activate

# Run Python command each 10 minutes
while true; do
    cd / && PYTHONPATH=. python /app/exporters/export.py to_postgis

    sleep 599
done

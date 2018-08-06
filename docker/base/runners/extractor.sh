#!/bin/bash

# Enable virtualenv
source $USER_HOME/.pyenv/versions/venv/bin/activate

# Run Python command each 60 seconds
watch -e -t -p -n 60 "python /app/"
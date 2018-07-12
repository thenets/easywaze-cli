#!/bin/bash

source $HOME/.bashrc

# Create virtualenv
if [ ! -f $HOME/.pyenv/versions/venv ]; then 
    pyenv virtualenv venv
    pyenv activate venv
    pip install --upgrade pip
fi

# Activate virtualenv
pyenv activate venv

# Update libs
pip install -r requirements.txt

# Run Python code
python main.py


#!/bin/bash

source $USER_HOME/.bashrc

set -x

# # Create virtualenv
# if [ ! -f $USER_HOME/.pyenv/versions/venv ]; then 
#     cd $USER_HOME/.pyenv/versions
#     virtualenv -p python3 venv
#     cd -
# fi

# # Activate virtualenv
# source $USER_HOME/.pyenv/versions/venv/bin/activate

# # Update libs
# pip install -r requirements.txt

# Run Python code
python main.py


#!/bin/bash

source $USER_HOME/.bashrc

# Main vars
ROOT_PATH=$(pwd)
VENV_PATH=$USER_HOME/.pyenv/versions/venv
SRC_PATH=src/
PIP_FILE=/app/requirements.txt

# Install dependencies
if [ -f $PIP_FILE ]; then
    md5_cache_file=$VENV_PATH/pip_md5.cache
    touch $md5_cache_file
    md5_cached=($(cat $md5_cache_file))
    md5=($(md5sum $PIP_FILE))

    # Install dependencies if not cached
    if [ ! "$md5" = "$md5_cached"  ]; then
        echo -e "$COLOR_CYAN# BAIXANDO DEPENDÊNCIAS$COLOR_DEFAULT"
        pip install -r $PIP_FILE
        echo ""
        # cache new hash
        echo $md5 > $md5_cache_file
    fi
fi

# Run Python code
set -x
python main.py


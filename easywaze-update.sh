#!/bin/bash

# Hello message
echo -e "\e[32m# Welcome to EasyWaze updater\e[0m"

# Check if is sudo
if [ "$EUID" -ne 0 ]
  then echo -e "\e[31m[ERROR] Please run as root\e[0m"
  exit
fi

export APP_NAME=easywaze

# Run main background process
docker rm -f $APP_NAME-main >/dev/null 2>/dev/null || true
docker run -d --restart=unless-stopped \
    --name $APP_NAME-main \
    -v /opt/easywaze/config.yaml:/app/config.yaml \
    --user=$USER_NAME \
    --network $APP_NAME \
    easywaze/extractor

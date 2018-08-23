#!/bin/bash

# Hello message
echo -e "\e[32m# Welcome to EasyWaze installer\e[0m"

# Check if is sudo
if [ "$EUID" -ne 0 ]
  then echo -e "\e[31m[ERROR] Please run as root\e[0m"
  exit
fi

export APP_NAME=easywaze

# Install docker
if ! [ -x "$(command -v docker)" ]; then
  "\e[33m# [WARN] Docker not found. Starting Docker installer...\e[0m"
  curl -sSL https://get.docker.io | sh
fi

# Install docker-compose
if ! [ -x "$(command -v docker-compose)" ]; then
  "\e[33m# [WARN] docker-compose not found. Downloading docker-compose installer...\e[0m"
  curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose
fi


# User prompt to get config data
echo "Type the city name (New York, São Paulo, ...):"
read CITY_NAME
echo "Type the country name (United States, Brazil, ...):"
read COUNTRY_NAME
echo "Type the Waze API endpoint (https://world-georss.waze.com/...):"
read ENDPOINT

# Generate config
echo -e "\e[32mGenerating new config file...\e[0m"
mkdir -p /opt/easywaze/
cat > /opt/easywaze/config.yaml <<_EOF_
cities:
- {city_name: '$CITY_NAME', country_name: '$COUNTRY_NAME', endpoint: '$ENDPOINT',
  }
_EOF_
chmod 777 /opt/easywaze/config.yaml


# DEBUG
#cat /opt/easywaze/config.yaml
#set -x
#exit

# Download latest EasyWaze image
echo -e "\e[32mDownload latest EasyWaze image...\e[0m"
docker pull easywaze/extractor

# Create network
echo -e "\e[32mCreating network...\e[0m"
docker network create $APP_NAME >/dev/null 2>/dev/null || true

# Added MySQL and phpMyAdmin
echo -e "\e[32mPreparing MySQL database and phpMyAdmin...\e[0m"
docker rm -f $APP_NAME-mysql $APP_NAME-phpmyadmin >/dev/null 2>/dev/null || true
mkdir -p /opt/$APP_NAME/mysql
echo -n $APP_NAME-mysql: 
docker run -d --name $APP_NAME-mysql --network=$APP_NAME \
            -e MYSQL_ROOT_PASSWORD="root" \
            -e MYSQL_DATABASE=$APP_NAME \
            -v /opt/$APP_NAME/mysql:/var/lib/mysql \
            -p 23306:3306 mysql:5.7.22
echo -n $APP_NAME-phpmyadmin:
docker run -d --name $APP_NAME-phpmyadmin -p 8000:80 \
            --network=$APP_NAME \
            -e PMA_HOST=$APP_NAME-mysql \
            phpmyadmin/phpmyadmin:edge

# Postgis
echo -e "\e[32mPreparing PostGIS database...\e[0m"
docker rm -f $APP_NAME-postgis >/dev/null 2>/dev/null || true
mkdir -p /opt/$APP_NAME/postgis
echo -n $APP_NAME-postgis:
docker run --name $APP_NAME-postgis --network=$APP_NAME \
            -e POSTGRES_USER=root \
            -e POSTGRES_PASS=root \
            -e POSTGRES_DBNAME=$APP_NAME \
            -e ALLOW_IP_RANGE=0.0.0.0/0 \
            -v /opt/$APP_NAME/postgis:/var/lib/postgresql \
            -p 25432:5432 -d -t kartoza/postgis
            
# Redis
echo -e "\e[32mPreparing Redis database...\e[0m"
docker rm -f $APP_NAME-redis >/dev/null 2>/dev/null || true
echo -n $APP_NAME-redis:
docker run --name $APP_NAME-redis --network=$APP_NAME \
-d -t redis:alpine

# Wating databases start
echo -e "\e[32mWating databases start...\e[0m"
sleep 30

# Run main background process
docker run -d --restart=unless-stopped \
    --name $APP_NAME-main \
    -v /opt/easywaze/config.yaml:/app/config.yaml \
    --user=$USER_NAME \
    --network $APP_NAME \
    easywaze/extractor

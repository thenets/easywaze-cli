#!/bin/sh

export APP_NAME=easywaze

set -x

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

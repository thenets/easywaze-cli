NAME = waze-ccp/capture
TAG = latest
SHELL = /bin/bash

USER_NAME=kratos
USER_HOME=/home/$(USER_NAME)
APP=/app
SOURCE_PATH=src
VOLUME_PATH=-v $(PWD)/$(SOURCE_PATH)/:/app/ \
			-v waze-venv:/home/kratos/.pyenv/versions

prepare:
	# Build Docker image
	make build 
	# Create volume for venv
	docker volume create waze-venv || true
	# Create database volume and dependencies
	make database

build: basics
	docker build -t $(NAME):$(TAG) --rm .

shell: basics
	docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--user=$(USER_NAME) \
		--network waze-ccp \
		$(NAME):$(TAG) $(SHELL)

shell-root: basics
	docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--network waze-ccp \
		$(NAME):$(TAG) $(SHELL)

run: start

start: basics
	docker run --rm -it \
		$(VOLUME_PATH) \
		-p 6000:6000 \
		--network waze-ccp \
		$(NAME):$(TAG)

basics:
	mkdir -p ./$(SOURCE_PATH)
 
database:
	docker volume create waze-ccp_database || true
	docker network create waze-ccp || true
	docker rm -f  db waze-ccp-phpmyadmin || true

	docker run -d --name db --network=waze-ccp -e MYSQL_ROOT_PASSWORD="root" -v waze-ccp_database:/var/lib/mysql mysql:5.7.22
	docker run -d --name waze-ccp-phpmyadmin -p 8000:80 --network=waze-ccp phpmyadmin/phpmyadmin:edge



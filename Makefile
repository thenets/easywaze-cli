NAME = waze-ccp/capture
TAG = latest
SHELL = /bin/bash

APP_NAME=waze

USER_NAME=kratos
USER_HOME=/home/$(USER_NAME)
APP=/app
SOURCE_PATH=src
VOLUME_PATH=-v $(PWD)/$(SOURCE_PATH)/:/app/ \
			-v $(APP_NAME)-venv:/home/kratos/.pyenv/versions

prepare:
	# Build Docker image
	make build 
	# Create volume for venv and fix permissions
	docker volume create $(APP_NAME)-venv || true
	docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		$(NAME):$(TAG) chown 1000.1000 /home/kratos/.pyenv/versions
	# Create database volume and dependencies
	make db

build: basics
	docker build -t $(NAME):$(TAG) --rm .

shell: basics
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--user=$(USER_NAME) \
		--network $(APP_NAME)-ccp \
		--name $(APP_NAME)-shell-$$RANDOM \
		$(NAME):$(TAG) $(SHELL)

shell-root: basics
	@echo -e "\e[91mMaking you a god...\e[0m"
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--name $(APP_NAME)-shellroot-$$RANDOM \
		--network $(APP_NAME)-ccp \
		$(NAME):$(TAG) $(SHELL)

run: start

start: basics
	@docker run --rm -it \
		$(VOLUME_PATH) \
		-p 6000:6000 \
		--user=$(USER_NAME) \
		--network $(APP_NAME)-ccp \
		$(NAME):$(TAG)

basics:
	@mkdir -p ./$(SOURCE_PATH)
 
db:
	@echo -e "\e[32mPreparing MySQL database...\e[0m"
	@docker volume create $(APP_NAME)-ccp_database || true
	@docker network create $(APP_NAME)-ccp || true
	@docker rm -f  db $(APP_NAME)-ccp-phpmyadmin || true
	@docker run -d --name db --network=$(APP_NAME)-ccp -e MYSQL_ROOT_PASSWORD="root" -v $(APP_NAME)-ccp_database:/var/lib/mysql mysql:5.7.22
	@docker run -d --name $(APP_NAME)-ccp-phpmyadmin -p 8000:80 --network=$(APP_NAME)-ccp phpmyadmin/phpmyadmin:edge

repair:
	@echo -e "\e[32mReparing...\e[0m"
	docker rm -f db $(docker container ls -af name=$(APP_NAME)) 2>/dev/null || true
	make basics
	make db
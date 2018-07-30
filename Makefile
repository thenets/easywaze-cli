NAME = thenets/easywaze
TAG = latest
SHELL = /bin/bash

APP_NAME=easywaze

USER_NAME=kratos
USER_HOME=/home/$(USER_NAME)
APP=/app
SOURCE_PATH=docker/base/src
VOLUME_PATH=-v $(PWD)/$(SOURCE_PATH)/:/app/ \
			-v $(APP_NAME)-venv:/home/kratos/.pyenv/versions


# Prepare the environment
# ==============================
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
	make services

	@echo ""
	@echo -e "\e[32mAll services working!\e[0m"
	@echo "$$SERVICES_INSTRUCTIONS"

# Docker builds
# ==============================
build: basics
	docker build -t $(NAME):$(TAG) --rm docker/base
	docker build -t $(NAME):master --rm docker/master
	docker build -t $(NAME):worker --rm docker/worker


# Interactive commands
# ==============================
shell: basics
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--user=$(USER_NAME) \
		--network $(APP_NAME) \
		--name $(APP_NAME)-shell-$$RANDOM \
		$(NAME):$(TAG) $(SHELL)

shell-root: basics
	@echo -e "\e[91mMaking you a god...\e[0m"
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--name $(APP_NAME)-shellroot-$$RANDOM \
		--network $(APP_NAME) \
		$(NAME):$(TAG) $(SHELL)


# Start master and worker mode
# ==============================
start-master: basics
	@docker run --rm -it \
		-v /opt/easywaze/config.yaml:/app/config.yaml \
		-p 6000:6000 \
		--user=$(USER_NAME) \
		--network $(APP_NAME) \
		$(NAME):$(TAG)

# Dependencies
# ==============================
define SERVICES_INSTRUCTIONS
- MySQL
| name : $(APP_NAME)-mysql
| user : root
| pass : root
| db   : $(APP_NAME)
| port : 23306
- phpMyAdmin
| name : $(APP_NAME)-phpmyadmin
| addr : http://127.0.0.1:8000/
- PostGIS
| name : $(APP_NAME)-postgis
| user : root
| pass : root
| db   : $(APP_NAME)
| port : 25432
endef
export SERVICES_INSTRUCTIONS
services:
	@# Create network
	@echo -e "\e[32mCreating network...\e[0m"
	@docker network create $(APP_NAME) >/dev/null 2>/dev/null || true

	@# Added MySQL and phpMyAdmin
	@echo -e "\e[32mPreparing MySQL database and phpMyAdmin...\e[0m"
	@docker rm -f $(APP_NAME)-mysql $(APP_NAME)-phpmyadmin >/dev/null 2>/dev/null || true
	@docker volume create $(APP_NAME)-mysql >/dev/null 2>/dev/null || true
	@echo -n $(APP_NAME)-mysql: 
	@docker run -d --name $(APP_NAME)-mysql --network=$(APP_NAME) \
				-e MYSQL_ROOT_PASSWORD="root" \
				-e MYSQL_DATABASE=$(APP_NAME) \
				-v $(APP_NAME)-mysql:/var/lib/mysql \
				-p 23306:3306 mysql:5.7.22
	@echo -n $(APP_NAME)-phpmyadmin:
	@docker run -d --name $(APP_NAME)-phpmyadmin -p 8000:80 \
				--network=$(APP_NAME) \
				-e PMA_HOST=$(APP_NAME)-mysql \
				phpmyadmin/phpmyadmin:edge

	@# Postgis
	@echo -e "\e[32mPreparing PostGIS database...\e[0m"
	@docker rm -f $(APP_NAME)-postgis >/dev/null 2>/dev/null || true
	@docker volume create $(APP_NAME)-postgis >/dev/null 2>/dev/null || true
	@echo -n $(APP_NAME)-postgis:
	@docker run --name $(APP_NAME)-postgis --network=$(APP_NAME) \
				-e POSTGRES_USER=root \
				-e POSTGRES_PASS=root \
				-e POSTGRES_DBNAME=$(APP_NAME) \
				-e ALLOW_IP_RANGE=0.0.0.0/0 \
				-v $(APP_NAME)-postgis:/var/lib/postgresql \
				-p 25432:5432 -d -t kartoza/postgis
				
	@# Redis
	@echo -e "\e[32mPreparing Redis database...\e[0m"
	@docker rm -f $(APP_NAME)-redis >/dev/null 2>/dev/null || true
	@echo -n $(APP_NAME)-redis:
	@docker run --name $(APP_NAME)-redis --network=$(APP_NAME) \
				-d -t redis:alpine
				

# Tools
# ==============================
basics:
	@mkdir -p ./$(SOURCE_PATH)

repair:
	@echo -e "\e[32mReparing...\e[0m"
	docker rm -f db $(docker container ls -af name=$(APP_NAME)) 2>/dev/null || true
	make basics
	make db
	



# Custom commands
# ==============================
cmd-capture:
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--user=$(USER_NAME) \
		--network $(APP_NAME) \
		--name $(APP_NAME)-shell-$$RANDOM \
		$(NAME):$(TAG) bin/capture.sh uygviuyvbiuvbiugbiugbviuygviv

cmd-export:
	@docker run --rm -it \
		$(VOLUME_PATH) \
		--entrypoint="" \
		--user=$(USER_NAME) \
		--network $(APP_NAME) \
		--name $(APP_NAME)-shell-$$RANDOM \
		$(NAME):$(TAG) bin/export.sh
FROM python:3.6.5-alpine3.7

ENV USER_NAME=kratos
ENV USER_HOME=/home/$USER_NAME
ENV APP=/app

USER root

RUN set -x && \
    # Install main packages
    apk add --no-cache git tar zip unzip bash make curl wget

# Create user
RUN adduser -D -u 501 -s /bin/bash $USER_NAME

# Create projeto dir
RUN set -x \
    && mkdir -p $APP \
    && mkdir -p $USER_HOME \
    && chown -R $USER_NAME.$USER_NAME $APP $USER_HOME

# Bash setup
RUN set -x \
    # Colorful root bash
    && echo 'export PS1="\e[1m\e[91mGodOfWar\e[39m:\e[96m\w\e[0m# "' > /root/.bashrc \
    # Colorful limited user bash
    && echo 'export PS1="\e[1m\e[32m\\u\e[39m@\e[34masgard\e[39m:\e[96m\w\e[0m$ "' > $USER_HOME/.bashrc \
    # Fix permissions
    && chown -R $USER_NAME.$USER_NAME $USER_HOME

# Python dependencies
RUN set -x \
    # MySQL / MariaDB
    && apk add --update --no-cache --virtual \
	    mariadb-client-libs build-deps mariadb-dev \
        gcc musl-dev mysql-client py-mysqldb \
    # pyenv dependencies
    && apk add --no-cache --update \
        build-base patch ca-certificates bzip2-dev linux-headers \
        ncurses-dev openssl openssl-dev readline-dev sqlite-dev

# Install pyenv
USER $USER_NAME
RUN set -x \
    && cd /tmp \
    && wget https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer \
    && chmod +x pyenv-installer \
    && ./pyenv-installer \
    && echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc \
    && echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc \
    && echo 'export PYENV_VIRTUALENV_DISABLE_PROMPT=1' >> ~/.bashrc \
    # HACK to fix volume permissions
    && mkdir -p $HOME/.pyenv/versions
USER root

WORKDIR $APP
ADD ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

VOLUME ['/home/kratos/.pyenv/versions']

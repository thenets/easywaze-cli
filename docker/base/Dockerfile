FROM ubuntu:18.04

ENV USER_NAME=kratos
ENV USER_HOME=/home/$USER_NAME
ENV APP=/app

RUN apt-get update && apt-get install -y \
        aufs-tools automake build-essential curl dpkg-sig libcap-dev \
        libsqlite3-dev virtualenv wget nano git \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN set -x \
    && groupadd -r -g 1000 $USER_NAME \
    && useradd -mr -c $USER_NAME -d $USER_HOME -g 1000 -u 1000 $USER_NAME

# Bash setup
RUN set -x \
    # Colorful root bash
    && echo 'export PS1="\e[1m\e[91mGodOfWar\e[39m:\e[96m\w\e[0m# "' > /root/.bashrc \
    # Colorful limited user bash
    && echo 'export PS1="\e[1m\e[32m\\u\e[39m@\e[34masgard\e[39m:\e[96m\w\e[0m$ "' > $USER_HOME/.bashrc \
    # HACK Alias from 'python' tp 'python3'
    && ln -s /usr/bin/python3 /usr/bin/python \
    # HACK to fix volume permissions
    && mkdir -p $USER_HOME/.pyenv/versions \
    # Create and start venv
    && echo 'if [ ! -d $USER_HOME/.pyenv/versions/venv ]; then ' >> $USER_HOME/.bashrc \
    && echo '    cd $USER_HOME/.pyenv/versions' >> $USER_HOME/.bashrc \
    && echo '    virtualenv -p python3 venv' >> $USER_HOME/.bashrc \
    && echo '    cd -' >> $USER_HOME/.bashrc \
    && echo 'fi' >> $USER_HOME/.bashrc \
    && echo 'source $USER_HOME/.pyenv/versions/venv/bin/activate' >> $USER_HOME/.bashrc \
    # Fix permissions
    && chown -R $USER_NAME.$USER_NAME $USER_HOME

# Add source code and install dependencies
RUN set -x \
    # Clone from remote repo
    && git clone https://github.com/CTS-FGV/easywaze.git /app \
    # Install virtualenv
    && cd $USER_HOME/.pyenv/versions \
    && virtualenv -p python3 venv \
    && chmod +x $USER_HOME/.pyenv/versions/venv/bin/activate \
    && . $USER_HOME/.pyenv/versions/venv/bin/activate \
    && cd /app \
    # Install dependencies
    && pip install -r requirements.txt

# Install supervisor
RUN set -x \
    && apt-get update && apt-get install -y supervisor \
    && apt-get clean all && apt-get autoclean \
    && apt-get autoremove -y \ 
    # Create log dir and Set permissions
    && mkdir -p /var/log/supervisor \
    && chown -R 1000.1000 /var/log/supervisor \
    # Create dir for runners
    && mkdir -p /etc/supervisor/conf.d/
# Add conf files
COPY supervisord.conf /etc/supervisord.conf
ADD ./runners/*.conf /etc/supervisor/conf.d/
ADD ./runners/*.sh /
ADD supervisord.conf /etc/supervisord.conf
# Fix permissions
RUN set -x \
    && chmod +x /*.sh \
    && mkdir -p /var/log/easywaze/

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

VOLUME ["/home/kratos/.pyenv/versions"]
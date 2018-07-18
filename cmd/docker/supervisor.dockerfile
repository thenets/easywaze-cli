FROM thenets/easywaze:latest

RUN set -x && \
    apk add --no-cache supervisor inotify-tools

ENTRYPOINT ["supervisord"]
CMD ["--nodaemon", "--configuration", "/etc/supervisord.conf"]
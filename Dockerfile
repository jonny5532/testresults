FROM python:3.12-alpine AS python

RUN apk add --no-cache rclone

WORKDIR /

ADD main.py testresults.py gitea.py entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]

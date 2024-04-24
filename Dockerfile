FROM python:3.12-slim-bullseye AS python

WORKDIR /

ADD main.py archives.py testresults.py entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]

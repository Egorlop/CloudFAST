FROM ubuntu:latest
LABEL authors="egorp"

ENTRYPOINT ["top", "-b"]
FROM ubuntu:latest
LABEL authors="chtg"

ENTRYPOINT ["top", "-b"]
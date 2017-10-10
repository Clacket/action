FROM python:3

ADD . /

RUN make minimal

RUN sh scripts/get_env_vars.sh

RUN flask db upgrade

RUN make run

EXPOSE 8000

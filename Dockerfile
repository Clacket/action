FROM python:3

ADD . /

RUN make minimal

RUN ls -a

RUN sh scripts/get_env.sh && flask db upgrade

RUN make run

EXPOSE 8000

FROM python:3

ADD . /

RUN make minimal

RUN flask db upgrade

RUN make run

EXPOSE 8000

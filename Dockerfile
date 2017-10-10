FROM python:3

ADD . /

RUN make minimal

flask db upgrade

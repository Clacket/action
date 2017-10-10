FROM python:3

ADD . /

RUN make minimal

CMD ["flask", "db", "upgrade"]

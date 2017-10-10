FROM python:3

ADD . /

RUN make minimal

RUN . scripts/get_env.sh && flask db upgrade

EXPOSE 8000

ENTRYPOINT ["make", "-B", "run"]
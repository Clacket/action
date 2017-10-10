FROM python:3

ADD . /

RUN make minimal

RUN ls -a

RUN . scripts/get_env.sh && flask db upgrade

EXPOSE 5000

ENTRYPOINT ["make", "-B", "run"]
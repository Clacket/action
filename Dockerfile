FROM amazon/aws-eb-python:3.4.2-onbuild-3.5.1

ADD . /

RUN make minimal

RUN ls -a

RUN . scripts/get_env.sh && flask db upgrade

EXPOSE 8000

ENTRYPOINT ["make", "-B", "run"]
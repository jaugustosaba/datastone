FROM debian:11

RUN apt update && apt install -y python3 python3-pip
RUN mkdir /datastone
COPY ./datastone/ /datastone
COPY ./requirements/base.txt /datastone
RUN pip install -r /datastone/base.txt
ENV DS_APP_NAME=datastone
ENV DS_AWESOME_API="https://economia.awesomeapi.com.br"
ENV DS_REFERENCE=USD
ENV DS_PORT=8080
ENV DS_REUSE_ADDR=false
ENV DS_LOG_LEVEL=INFO
ENV DS_RELOAD_TIMEOUT=300
CMD python3 -m datastone \
    --app-name ${DS_APP_NAME} \
    --awesome-api ${DS_AWESOME_API} \
    --reference ${DS_REFERENCE} \
    --port ${DS_PORT} \
    --reuse-address ${DS_REUSE_ADDR} \
    --log-level ${DS_LOG_LEVEL} \
    --reload-timeout ${DS_RELOAD_TIMEOUT}
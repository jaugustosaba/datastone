FROM debian:11

RUN apt update && apt install -y python3 python3-pip
RUN mkdir /datastone
COPY ./main.py /datastone
COPY ./requirements/base.txt /datastone
RUN pip install -r /datastone/base.txt
RUN pip freeze
ENTRYPOINT [ "python3", "/datastone/main.py"]

FROM ubuntu:latest

RUN mkdir /usr/src/app
WORKDIR /usr/src/app/

COPY ./requirements.txt .

RUN apt-get update && apt-get install -y python3-pip git

RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1

COPY . .

WORKDIR /usr/src/app/src

ENTRYPOINT [ "python3", "-m", "unittest", "-v"]

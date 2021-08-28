FROM ubuntu

RUN mkdir /usr/src/app
WORKDIR /usr/src/app/

COPY ./requirements.txt .

# Installing python and git
RUN apt-get update && apt-get install -yq python3-pip git 

# Installing nodejs and npm
RUN apt-get install -y curl 
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install nodejs

# Showdown setup
WORKDIR /usr/src
RUN git clone https://github.com/smogon/pokemon-showdown.git
RUN cp pokemon-showdown/config/config-example.js pokemon-showdown/config/config.js
WORKDIR /usr/src/pokemon-showdown
# RUN ./pokemon-showdown

# Python setup
WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app/src

ENTRYPOINT [ "python3", "-m", "unittest", "-v" ]
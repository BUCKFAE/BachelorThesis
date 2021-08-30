FROM ubuntu

RUN mkdir /usr/showdown
WORKDIR /usr/showdown

# Installing python and git
RUN apt-get update && apt-get install -yq git 

# Installing nodejs and npm
RUN apt-get install -y curl 
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Showdown setup
RUN git clone https://github.com/smogon/pokemon-showdown.git
RUN cp pokemon-showdown/config/config-example.js pokemon-showdown/config/config.js
WORKDIR /usr/src/pokemon-showdown
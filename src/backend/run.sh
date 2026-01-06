#!/bin/bash

sudo docker rm -f kpo_back &&
sudo docker build -t back . &&
  sudo docker run --name kpo_back \
    --network=kpo_net \
    -e POSTGRES_PASSWORD=${KPO_POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${KPO_POSTGRES_DB} \
    -e POSTGRES_USER=${KPO_POSTGRES_USER} \
    -e POSTGRES_HOST=${KPO_POSTGRES_HOST} \
    -e POSTGRES_PORT=${KPO_POSTGRES_PORT} \
    -d -p 1337:8080 back

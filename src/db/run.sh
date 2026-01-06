#!/bin/bash

sudo docker rm -f kpo_pdb &&
sudo docker build -t pdb . &&
  sudo docker run \
  --name kpo_pdb \
  --network kpo_net \
  -e POSTGRES_PASSWORD=${KPO_POSTGRES_PASSWORD} \
  -d -p 5432:5432 pdb
  #sudo docker run --net kpo_net -p 5432:5432 pdb

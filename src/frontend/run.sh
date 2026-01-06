#!/bin/bash

sudo docker rm -f kpo_front &&
sudo docker build -t front . &&
  sudo docker run --name kpo_front \
  --network=kpo_net \
  -e TERM=${KPO_TERM} \
  -it front

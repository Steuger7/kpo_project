#!/bin/bash

sudo docker rm -f kpo_back &&
sudo docker build -t back .

#!/bin/bash

sudo docker rm -f kpo_pdb &&
sudo docker build -t pdb .

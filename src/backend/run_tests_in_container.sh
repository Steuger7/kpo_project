#!/bin/bash

sudo docker exec kpo_back npm run test:unit &&
  sudo docker exec kpo_back npm run test:integration

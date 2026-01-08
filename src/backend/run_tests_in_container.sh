#!/bin/bash

sudo docker exec kpo_back npm run test:unit &&
  sudo docker exec kpo_back node --experimental-vm-modules ./test/integration/integration_test.js

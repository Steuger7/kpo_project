#!/bin/bash

kill_children() {
  local child_pid=($(pgrep -P $1))

  if [[ -z "$child_pid" ]]; then
    return 0
  else 
    kill_children $child_pid
  fi

  kill -9 $child_pid
}

run_test() {
  local program_path="$(dirname $0)"
  POSTGRES_DB=${KPO_POSTGRES_DB} \
    POSTGRES_USER=${KPO_POSTGRES_USER} \
    POSTGRES_HOST=${KPO_POSTGRES_HOST} \
    POSTGRES_PORT=${KPO_POSTGRES_PORT}  \
    POSTGRES_PASSWORD=${KPO_POSTGRES_PASSWORD} npm run devstart --prefix ${program_path}/../../ &
  local pid="$!"

  sleep 2
  echo ""

  ${program_path}/clean_up.sh > /dev/null
  HOST=http://${KPO_POSTGRES_HOST}:${KPO_APP_PORT}/ node --experimental-vm-modules integration_test.js

  kill_children $pid
  kill -9 $pid
}
  
  KPO_POSTGRES_DB="libralib" \
  KPO_POSTGRES_USER="postgres" \
  KPO_POSTGRES_HOST="localhost" \
  KPO_POSTGRES_PASSWORD="docker" \
  KPO_POSTGRES_PORT="5432" \
  KPO_APP_PORT="3030" run_test

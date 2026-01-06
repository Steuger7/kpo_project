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
  POSTGRES_DB=$DB POSTGRES_USER=$PGUSER POSTGRES_HOST=$PGHOST POSTGRES_PORT=5432 POSTGRES_PASSWORD=$PGPASSOWRD npm run devstart --prefix ${program_path}/../../ &
  local pid="$!"

  sleep 2
  echo ""

  ${program_path}/clean_up.sh > /dev/null
  HOST=http://${PGHOST}:${APP_PORT}/ node --experimental-vm-modules test/integration/integration_test.js

  kill_children $pid
  kill -9 $pid
}

run_test

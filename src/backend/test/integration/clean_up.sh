#!/bin/bash

do_cleanup() {
  psql -U $PGUSER -d $DB -h $PGHOST -c "DELETE FROM users WHERE username = hash_string('s');"
}

do_cleanup

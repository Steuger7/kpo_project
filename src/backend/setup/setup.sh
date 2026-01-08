#!/bin/bash

root_dir="$(dirname $0)/.."
sql_dir="$root_dir/../db"
db_name="libralib"

echo "creating database..."
sudo -u postgres psql -f $sql_dir/create_db.sql

echo "doing setup of database..."
sudo -u postgres psql -d $db_name -f $sql_dir/install_pgcrypto.sql

sudo -u postgres psql -d $db_name -f $sql_dir/create_tables.sql -f $sql_dir/functions/verify_user.sql -f $sql_dir/procedures/append_book.sql -f $sql_dir/triggers/forbid_more_books.sql

echo "Done..."
cd "$root_dir"
npm install

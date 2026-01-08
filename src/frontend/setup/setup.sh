#!/bin/bash

echo "Установка зависимостей для LibApp..."

venv_name="venv"
setup_dir=$(dirname $0)
python3 -m venv ${setup_dir}/../${venv_name}
. ${setup_dir}/../${venv_name}/bin/activate
pip3 install textual requests

echo "Установка завершена"


echo "Запуск LibApp.py"

main_dir="${setup_dir}/.."
python3 ${main_dir}/LibApp.py

echo ""
echo "/////////////////////////////"
echo ""
echo "Для запуска используйте следующую команду в frontend (cd ..):"
echo "python3 LibApp.py"
echo ""
echo "/////////////////////////////"

deactivate

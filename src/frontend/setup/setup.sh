#!/bin/bash

echo "Установка зависимостей для LibApp..."

pip install textual
pip install python-dotenv
pip install requests

echo "Установка завершена"

echo ""
echo "/////////////////////////////"
echo ""
echo "Для запуска используйте следующую команду в frontend:"
echo "python3 LibApp.py"
echo ""
echo "/////////////////////////////"

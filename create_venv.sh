#!/bin/bash

python3.6 -m venv env
source env/bin/activate
pip install -r requirements.txt
./manage.py init_db
./manage.py collectstatic

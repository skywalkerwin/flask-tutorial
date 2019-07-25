#! /bin/bash
python3 -m venv venv
. venv/bin/activate
export FLASK_APP=flaskr
export FLASK_ENV=development
flask init-db
flask run
#!/bin/sh
# shellcheck disable=SC2164
cd /salesync/consulting_service

flask db init
flask db migrate
flask db upgrade

gunicorn --bind 0.0.0.0:5000 --timeout 90 "app:create_app()"
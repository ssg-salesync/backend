#!/bin/bash

rollback_and_init_migration() {
    flask db downgrade base
    flask db init
}

migrate() {
    flask db migrate
}

run_app() {
    gunicorn --bind 0.0.0.0:5000 --timeout 90 "app:create_app()"
}

main() {
    # shellcheck disable=SC2164
    cd /salesync/consulting_service

    migrate_status=$(flask db migrate 2>&1)
    if [[ $migrate_status == *"Can't locate revision identified by"* ]]; then
        rollback_and_init_migration
        migrate
    fi

    run_app
}

main
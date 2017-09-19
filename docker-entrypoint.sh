#!/bin/bash

echo "$(python -V)"
echo "MySql version: $(mysql -V)"

echo "Start MySql service..."
etc/init.d/mysql start

database() {
    DATABASE_NAME='reports_data'
    DATABASE_USER='root'
    DATABASE_USER_PASSWORD='root'

    database_name=$(awk -F "=" '/database_name/ {print $2}' /usr/src/reports.brokers/auth.ini)
    database_user=$(awk -F "=" '/database_user/ {print $2}' /usr/src/reports.brokers/auth.ini)
    database_user_password=$(awk -F "=" '/database_user_password/ {print $2}' /usr/src/reports.brokers/auth.ini)

    if [ ! -z "${database_name// }" ]; then
        DATABASE_NAME=$database_name
    fi

    if [ ! -z "${database_user// }" ]; then
        DATABASE_USER=$database_user
    fi 

    if [ ! -z "${database_user_password// }" ]; then
        DATABASE_USER_PASSWORD=$database_user_password
    fi

    echo "Create database '$DATABASE_NAME'..."
    mysql -uroot -e "CREATE DATABASE IF NOT EXISTS $DATABASE_NAME;"

    echo "Create database user: $DATABASE_USER, with password..."
    mysql -uroot -e "CREATE USER IF NOT EXISTS '$DATABASE_USER'@'localhost' IDENTIFIED BY '$DATABASE_USER_PASSWORD';"
    mysql -uroot -e "GRANT ALL PRIVILEGES ON $DATABASE_NAME.* TO '$DATABASE_USER'@'localhost';"
    mysql -uroot -e "FLUSH PRIVILEGES;"

    echo "Create database schema..."
    mysql -uroot $DATABASE_NAME < /usr/src/reports.brokers/reports/brokers/database/reports_data_dev.sql
}

run() {
    cd /usr/src/reports.brokers && source .env/bin/activate && ./bin/circusd
}

database
run

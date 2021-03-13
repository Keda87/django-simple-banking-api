#!/bin/bash

#------------ Usage details for shell script starts here ----------------
usage()
{
  echo
  echo "Usage: $0 -s -k -t -h"
  echo
  echo "    -s start service"
  echo "    -k stop service"
  echo "    -t run tests"
  echo "    -h this text"
  echo
}

while getopts ':skth' opt; do
    case $opt in
        s)  START_SERVICE=1
            ;;
        k)  STOP_SERVICE=1
            ;;
        t)  RUN_TESTS=1
            ;;
        h)  usage
            exit 1
            ;;
    esac
done
#------------ Usage details for shell script ends here ----------------

#------------- Code to start service starts here ---------------
if [[ ${START_SERVICE} -eq "1" ]]; then
  echo "Starting banking system service..."
  docker-compose up -d

  BANK_API_CONTAINER_ID=$(docker ps --filter "name=bank_api-container" -q)
  BANK_DB_CONTAINER_ID=$(docker ps --filter "name=bank_db-container" -q)
  REVERSE_PROXY_CONTAINER_ID=$(docker ps --filter "name=reverse_proxy-container" -q)

  if [[ -z ${REVERSE_PROXY_CONTAINER_ID} ]]; then
    echo "Could not start bank system reverse proxy"
    exit 5
  fi

  if [[ -z ${BANK_API_CONTAINER_ID} ]]; then
    echo "Could not start bank system"
    exit 5
  fi

  if [[ -z ${BANK_DB_CONTAINER_ID} ]]; then
    echo "Could not start bank db"
    exit 5
  fi

  echo "Creating the bank database and performing migrations..."

  docker-compose exec bank_db createdb --username=postgres db_banking
  docker-compose exec bank_api python manage.py migrate
  docker-compose exec bank_api python manage.py collectstatic
fi
#------------- Code to start service ends here ---------------

#------------- Code to stop service starts here ---------------
if [[ ${STOP_SERVICE} -eq "1" ]]; then
  docker-compose down
fi
#------------- Code to stop service ends here ---------------

#------------- Code to run tests starts here ---------------
if [[ ${RUN_TESTS} -eq "1" ]]; then
  BANK_API_CONTAINER_ID=$(docker ps --filter "name=bank_api-container" -q)
  BANK_DB_CONTAINER_ID=$(docker ps --filter "name=bank_db-container" -q)
  REVERSE_PROXY_CONTAINER_ID=$(docker ps --filter "name=reverse_proxy-container" -q)

  if [[ -z ${REVERSE_PROXY_CONTAINER_ID} ]]; then
    echo "Bank system reverse proxy is not up. Cannot run tests"
    exit 5
  fi

  if [[ -z ${BANK_API_CONTAINER_ID} ]]; then
    echo "Bank system api is not up. Cannot run tests"
    exit 5
  fi

  if [[ -z ${BANK_DB_CONTAINER_ID} ]]; then
    echo "Bank system db is not up. Cannot run tests"
    exit 5
  fi

  docker-compose exec bank_api python manage.py test --keepdb
fi
#------------- Code to run tests ends here ----------------
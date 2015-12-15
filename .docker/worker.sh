#!/bin/bash
source /usr/local/bin/config_env

PRE=""
CELERY_QUEUES=${CELERY_QUEUES:-celery}
CMD="python manage.py celery worker -Q $CELERY_QUEUES --scheduler=djcelery.schedulers.DatabaseScheduler --loglevel=DEBUG -E $CELERY_OPTS"

cd $APP_DIR
if [ ! -z "$NEW_RELIC_LICENSE_KEY" ] ; then
    pip install -U newrelic
    PRE="newrelic-admin run-program "
fi

echo "Starting Worker..."
echo $PRE $CMD
exec $PRE $CMD

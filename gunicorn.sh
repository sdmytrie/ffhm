#!/bin/bash

# kill -9 $(ps -ef | grep [g]unicorn | awk '{print $2}')
set -e
LOGFILE=/opt/www/ffhm.dmytrienko.tld/logs/gunicorn/ffhm.log
LOGDIR=$(dirname $LOGFILE)
LOGLEVEL=debug   # info ou warning une fois l'installation OK
NUM_WORKERS=9    # Règle : (2 x $num_cores) + 1
#NUM_THREADS=3    # Règle : (2 x $num_cores) + 1

# user/group to run as
USER=root
GROUP=root

cd /opt/www/ffhm.dmytrienko.tld/site/
source /opt/www/ffhm.dmytrienko.tld/ffhmenv/bin/activate  # Cette ligne ne sert que si vous utilisez virtualenv
test -d $LOGDIR || mkdir -p $LOGDIR
exec gunicorn ffhm.wsgi:application --workers=$NUM_WORKERS \
	  --user=$USER --group=$GROUP --log-level=$LOGLEVEL \
	    --log-file=$LOGFILE 2>>$LOGFILE -b 127.0.0.1:8000 \
	    --timeout 300 \
	    --daemon

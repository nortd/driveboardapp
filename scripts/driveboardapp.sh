#!/bin/bash
# place in: /etc/init.d/driveboardapp.sh
# make executable: sudo chmod 755 /etc/init.d/driveboardapp.sh
# activate with: sudo update-rc.d driveboardapp.sh defaults
# deactivate with: sudo update-rc.d -f driveboardapp.sh remove

LASAURAPP="/root/driveboardapp/backend/app.py"
LASAURPROC="driveboardapp\/backend\/app\.py"

case "$1" in
    start)
    echo "Starting driveboardapp ..."
    echo -n "at "
    date
    /usr/bin/python $LASAURAPP 
    ;;

    stop)
    echo "Stopping driveboardapp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    ;;

    restart)
    echo "Restarting driveboardapp ..."
    echo "Stopping driveboardapp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    echo "Starting driveboardapp ..."
    /usr/bin/python $LASAURAPP 
    ;;

    debug)
    echo "Restarting driveboardapp in debug mode..."
    echo "Stopping driveboardapp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    echo "Starting driveboardapp with --debug ..."
    /usr/bin/python $LASAURAPP --debug
    ;;

    *)
    echo "Usage: /etc/init.d/driveboardapp.sh {start|stop|restart|debug}" >&2
    exit 1
esac



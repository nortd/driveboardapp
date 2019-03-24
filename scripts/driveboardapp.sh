#!/bin/sh
# kFreeBSD do not accept scripts as interpreters, using #!/bin/sh and sourcing.
if [ true != "$INIT_D_SCRIPT_SOURCED" ] ; then
    set "$0" "$@"; INIT_D_SCRIPT_SOURCED=true . /lib/init/init-d-script
fi
### BEGIN INIT INFO
# Provides:          Driveboardapp
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: current Lasersaur software
# Description:       version 17.04
#
### END INIT INFO

# Author: Stefan Hechenberger <stefan@nortd.com>
#
# Please remove the "Author" lines above and replace them
# with your own name if you copy and modify this script.

DESC="Lasersaur Server"
DAEMON="/root/driveboardapp/backend/app.py"


# original documentation
# place in: /etc/init.d/driveboardapp.sh
# make executable: sudo chmod 755 /etc/init.d/driveboardapp.sh
# activate with: sudo update-rc.d driveboardapp.sh defaults
# deactivate with: sudo update-rc.d -f driveboardapp.sh remove

LASAURPROC="driveboardapp\/backend\/app\.py"

case "$1" in
    start)
    echo "Starting driveboardapp ..."
    echo -n "at "
    date
    /usr/bin/python $DAEMON 
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
    /usr/bin/python $DAEMON 
    ;;

    debug)
    echo "Restarting driveboardapp in debug mode..."
    echo "Stopping driveboardapp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    echo "Starting driveboardapp with --debug ..."
    /usr/bin/python $DAEMON --debug
    ;;

    *)
    echo "Usage: /etc/init.d/driveboardapp.sh {start|stop|restart|debug}" >&2
    exit 1
esac



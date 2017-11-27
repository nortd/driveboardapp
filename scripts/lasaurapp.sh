#!/bin/sh
# kFreeBSD do not accept scripts as interpreters, using #!/bin/sh and sourcing.
if [ true != "$INIT_D_SCRIPT_SOURCED" ] ; then
    set "$0" "$@"; INIT_D_SCRIPT_SOURCED=true . /lib/init/init-d-script
fi
### BEGIN INIT INFO
# Provides:          LasaurApp
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: original Lasersaur software, deprecated
# Description:       Control the lasersaur software through version
#                    15.00
### END INIT INFO

# Author: Stefan Hechenberger <stefan@nortd.com>
#
# Please remove the "Author" lines above and replace them
# with your own name if you copy and modify this script.

DESC="LasaurApp Server"
DAEMON="/usr/bin/python /root/LasaurApp/backend/app.py -p --beaglebone"

# original documentation
# place in: /etc/init.d/lasaurapp.sh
# make executable: sudo chmod 755 /etc/init.d/lasaurapp.sh
# activate with: sudo update-rc.d lasaurapp.sh defaults
# deactivate with: sudo update-rc.d -f lasaurapp.sh remove

LASAURAPP="/root/LasaurApp/backend/app.py"
LASAURPROC="LasaurApp\/backend\/app\.py"

case "$1" in
    start)
    echo "Starting LasaurApp ..."
    /usr/bin/python $LASAURAPP -p --beaglebone
    ;;

    stop)
    echo "Stopping LasaurApp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    ;;

    restart)
    echo "Restarting LasaurApp ..."
    echo "Stopping LasaurApp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    echo "Starting LasaurApp ..."
    /usr/bin/python $LASAURAPP -p --beaglebone
    ;;

    debug)
    echo "Restarting LasaurApp in debug mode..."
    echo "Stopping LasaurApp ..."
    ps ax | awk "/$LASAURPROC/ "'{ system("kill " $1) }'
    echo "Starting LasaurApp ..."
    /usr/bin/python $LASAURAPP -p --beaglebone --debug
    ;;

    *)
    echo "Usage: /etc/init.d/lasersaur {start|stop|restart|debug}" >&2
    exit 1
esac

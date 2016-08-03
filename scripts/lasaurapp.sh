#!/bin/bash
# place in: /etc/init.d/lasaurapp.sh
# make executable: sudo chmod 755 /etc/init.d/lasaurapp.sh
# activate with: sudo update-rc.d lasaurapp.sh defaults
# deactivate with: sudo update-rc.d -f lasaurapp.sh remove

if test "$1" = "start"
then
    echo "Starting LasaurApp ..."
    /usr/bin/python /root/LasaurApp/backend/app.py -p --beaglebone
fi

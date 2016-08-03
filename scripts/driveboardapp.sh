#!/bin/bash
# place in: /etc/init.d/driveboardapp.sh
# make executable: sudo chmod 755 /etc/init.d/driveboardapp.sh
# activate with: sudo update-rc.d driveboardapp.sh defaults
# deactivate with: sudo update-rc.d -f driveboardapp.sh remove

if test "$1" = "start"
then
    echo "Starting DriveboardApp ..."
    /usr/bin/python /root/driveboardapp/backend/app.py
fi

#!/bin/sh

echo "Switching from DriveboardApp to LasaurApp ..."

update-rc.d -f driveboardapp.sh remove

cp /root/driveboardapp/scripts/lasaurapp.sh /etc/init.d/lasaurapp.sh
chmod 755 /etc/init.d/lasaurapp.sh
update-rc.d lasaurapp.sh defaults

echo "Done!"

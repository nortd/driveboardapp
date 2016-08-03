

echo "Switching from DriveboardApp to LasaurApp ..."

update-rc.d -f driveboardapp.sh remove
update-rc.d lasaurapp.sh defaults

echo "Done!"

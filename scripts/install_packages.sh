#!/bin/bash

echo "installing python-imaging ..."
echo "Updating sources.list (backup in /etc/apt/sources.list.old)"
mv /etc/apt/sources.list /etc/apt/sources.list.old
cp sources.list /etc/apt/sources.list
apt-get update
apt-get install python-imaging
echo "Done!"

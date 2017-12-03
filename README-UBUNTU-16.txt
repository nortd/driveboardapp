jet@allartburns.org
3 Dec 2017


Two options

1) just install Ubuntu-16 on a fresh SD card and run the install script

2) run the wrong way in traffic and upgrade your existing build

Part the First, Update Ubuntu via SSH (not for the faint of heart)
These are the steps I took.  When I tried a similar set of steps on my
dev machine they failed for all sorts of wobbly reasons.  On my "real"
lasersaur it just worked:

apt-get update
apt-get upgrade
apt-get dist-upgrade  # probalby not needed
apt-get install update-manager-core
screen -S upgrade
#
#  IMPORTANT:  It's possible you have too many packages installed
#  and don't have room for the upgrader to download the next release.
#  Be ready to apt remove a lot of stuff you can reinstall after the
#  upgrade.  I had to remove emacs, gcc, g++, x11 (how did that get
# installed?) then do autoclean to make room for the upgrade.
#
do-release-upgrade
# now ssh in to the new port from another terminal and reattach to
# the screen service to maintain the conneciton after the stock
# sshd is restarted
screen -x upgrade
# then when it's all done:
shutdown -r now


Part the Second, Update driveboardapp:

switch to my repo:
https://github.com/allartburns/driveboardapp
checkout branch "ubuntu-16"
then re-install

cd /root/driveboardapp/scripts
./upgrade_to_driveboardapp.sh
shutdown -r now


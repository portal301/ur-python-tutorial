#!/bin/sh
# 
# file   urmagic_x11vnc.sh
# author Damien LETARD <dle@pygmatec.com>
# modified Yuvarajoo <yuva@deltaglobal.com.my>
# Script d'installation du serveur vnc en service
# ajp add library file check
# kaha add xsession modification and reboot at the end
# VNC and Libs updated by David Sadek <dasa@universal-robots.com>
#
LOGGER=/usr/bin/logger


log() {
    $LOGGER -p user.info -t "$0[$$]" -- "$1"
}

if [ "$1" = "" ] ; then
    log "no mountpoint supplied, exiting."
    exit 1 ; fi

MOUNTPOINT=$1

log "Point de montage : $MOUNTPOINT" 

# Check if first line of ~/xsession is #!/bin/bash
input="#!/bin/bash"
firstline="$(head -1 ~/xsession)"
# Display for test purposes. To be commented out
#echo "$input" | DISPLAY=:0 aosd_cat -R red -x 130 -y -210 -n "Arial Black 40"
#echo "$firstline" | DISPLAY=:0 aosd_cat -R red -x 130 -y -210 -n "Arial Black 40"

if [ "$input" != "$firstline" ]
then
	# Inform user VNC already installed and exit
	echo "! VNC already installed, Please remove USB !" | DISPLAY=:0 aosd_cat -R red -x 130 -y -210 -n "Arial Black 40"
	exit 1
fi

if [ -e $MOUNTPOINT/package/libtcl8.6_8.6.2+dfsg-2_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/libtk8.6_8.6.2-1_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/libvncclient0_0.9.9+dfsg2-6.1+deb8u3_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/libvncserver0_0.9.9+dfsg2-6.1+deb8u3_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/libxft2_2.3.2-1_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/screen_4.2.1-3+deb8u1_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/tcl_8.6.0+8_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/tcl8.6_8.6.2+dfsg-2_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/tk_8.6.0+8_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/tk8.6_8.6.2-1_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/x11vnc_0.9.13-1.2+b2_i386.deb ] &&\
   [ -e $MOUNTPOINT/package/x11vnc-data_0.9.13-1.2_all.deb ] &&\
   [ -e $MOUNTPOINT/script/x11vnc ]
then
    # Warn user not to remove USB key
	echo "! Installing VNC Server !" | DISPLAY=:0 aosd_cat -R red -x 130 -y -210 -n "Arial Black 40"
else
    # Inform user library files missing and exit
	echo "! Required Files Missing, Exiting !" | DISPLAY=:0 aosd_cat -R red -x 130 -y -210 -n "Arial Black 40"
	exit 1
fi

for FILE in `find $MOUNTPOINT/package/ -name *.deb`; do
  log "Package trouve : $FILE"
done 

# Install all necessary packages
su -c "dpkg -i $MOUNTPOINT/package/*.deb"

# Create vnc folder
su -c "mkdir /root/.vnc"
# Generate password for VNC connection -- default password "easybot" change following to any personal passwords
su -c "/usr/bin/x11vnc -storepasswd easybot /root/.vnc/passwd"

# Copy vnc scripts
su -c "cp $MOUNTPOINT/script/x11vnc /etc/init.d/"
su -c "chmod u+x /etc/init.d/x11vnc"

# Register service
su -c "update-rc.d x11vnc defaults"

# Start vnc service
su -c "/etc/init.d/x11vnc start"


# Make sure data is written to the USB key
sync
sync

# Editing~/xsession
cat ~/xsession > ~/tempfile
echo "/usr/bin/x11vnc -xkb -noxrecord -noxfixes -noxdamage -display :0 -rfbauth /etc/x11vnc.pass -rfbport 5900 -forever -auth root -bg -o /var/log/x11vnc.log" > ~/xsession
cat ~/tempfile >> ~/xsession

# Notify user it is ok to remove USB key and displays current password
echo "VNC Successfully Installed" | DISPLAY=:0 aosd_cat -x 130 -y -210 -n "Arial Black 40"
echo "Password 'easybot'" | DISPLAY=:0 aosd_cat -x 130 -y -210 -n "Arial Black 40"

# Rebooting
echo "Rebooting in 3 seconds. Remove USB immediately after robot shutdown!" | DISPLAY=:0 aosd_cat -x 130 -y -210 -n "Arial Black 40"
sleep 3
reboot
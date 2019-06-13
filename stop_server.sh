#!/bin/bash

# This stops the server if there is no one logged
# in for an hour (ish).
#
# This depends on the sshd_config file enforcing idle timouts
# based on 1 hour
#
# We use /dev/shm for our count file because /dev/shm is in memory
# and will clear on reboot / startup.
#
# Put in /usr/local/sbin and add to cron:
# */5 * * * * /usr/local/sbin/stop_server.sh 2>&1 > /dev/null

# Check to see if anyone is logged on
current=$( /usr/bin/w -h |/usr/bin/wc -l )
load=$( cat /proc/loadavg | awk '{print $2}' | awk -F. '{print $1}' )

if (( $current > 0 )); then
  /usr/bin/logger "SAVER - $current accounts logged in"
  exit 0
fi

# Don't stop the server if there is load on it.
if (( $load > 0 )); then
  /usr/bin/logger "SAVER - Current load average is $load"
  exit 0
fi

# Pull in the temp file value as a var
if [ ! -f /dev/shm/.count ]; then
  echo 1 > /dev/shm/.count
  count=1
else
  count=$( cat "/dev/shm/.count" )
fi

/usr/bin/logger "SAVER - No one logged in for $count intervals"

# Check temp file, if this is 12, then shutdown
if (( $count > 11 )); then
  /usr/bin/logger "SAVER - Reached 12 checks - HALTING SYSTEM"
  /usr/sbin/shutdown -h now
else
  ((count++))
  echo $count > /dev/shm/.count
fi

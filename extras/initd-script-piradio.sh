#!/bin/sh
#/etc/init.d/piradio

### BEGIN INIT INFO
# Provides:          piradio
# Required-Start:    $remote_fs $syslog $network $all
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Piradio client
# Description:       Piradio client
### END INIT INFO

# If you want a command to always run, put it here

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting piradio"
    # run application you want to start
    cd /home/pi/piradio
    nohup python piradio.py 1>> "/var/log/piradio.log" 2>&1& echo $! > "/var/pids/piradio.pid"
    ;;
  stop)
    echo "Stopping piradio"
    # kill application you want to stop
    sudo kill `cat /var/pids/piradio.pid`
    ;;
  *)
    echo "Usage: /etc/init.d/piradio {start|stop}"
    exit 1
    ;;
esac

exit 0

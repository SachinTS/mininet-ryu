#!/bin/bash

echo Starting OVS for $1
ovs-vswitchd unix:/tmp/mininet-$1/db.sock \
-vconsole:info \
-vsyslog:err \
-vfile:dbg \
--mlockall \
--no-chdir \
--log-file=/tmp/mininet-$1/ovs-vswitchd.log \
--pidfile=/tmp/mininet-$1/ovs-vswitchd.pid \
--detach \
--monitor

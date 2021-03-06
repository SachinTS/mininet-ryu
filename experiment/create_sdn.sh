#!/bin/bash

echo Configure OVS for $1
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-br $1
for port in $(netstat -i | grep $1- | cut -d' ' -f 1);
do
  echo adding $port;
  ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-port $1 $port
done
#ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-port $1 $1-eth1
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock set bridge $1 protocols=OpenFlow13
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock set-fail-mode $1 secure
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock set-controller $1 tcp:10.0.0.95:6653
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock show

# # set logging setting
# ovs-appctl vlog/set file:vconn:dbg
# ovs-appctl vlog/set file:dpif:dbg
# ovs-appctl vlog/set file:ofp_msgs:dbg
# ovs-appctl vlog/set file:memory:dbg
# ovs-appctl vlog/set file:flow:dbg

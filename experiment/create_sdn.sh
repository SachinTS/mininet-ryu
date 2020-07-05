#!/bin/bash

echo Configure OVS for $1
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-br $1
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-port $1 $1-eth0
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock add-port $1 $1-eth1
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock set-fail-mode $1 secure
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock set-controller $1 tcp:127.0.0.1:6633
ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock show

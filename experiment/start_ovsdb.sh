#!/bin/bash

echo Starting OVSDB for $1
mkdir -p /tmp/mininet-$1

if [ -e /tmp/mininet-$1/conf.db ]; then
   echo DB already exists
   echo deleting...
   kill -9 `ps -ef | grep /tmp/mininet | grep -v grep | awk '{ print $2 }'` 
   rm -rf /tmp/mininet-$1/*
fi
echo Createing OVSDB
ovsdb-tool create /tmp/mininet-$1/conf.db /usr/share/openvswitch/vswitch.ovsschema

ovsdb-server /tmp/mininet-$1/conf.db \
-vconsole:emer \
-vsyslog:err \
-vfile:info \
--remote=punix:/tmp/mininet-$1/db.sock \
--private-key=db:Open_vSwitch,SSL,private_key \
--certificate=db:Open_vSwitch,SSL,certificate \
--bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
--no-chdir \
--log-file=/tmp/mininet-$1/ovsdb-server.log \
--pidfile=/tmp/mininet-$1/ovsdb-server.pid \
--detach \
--monitor

ovs-vsctl --db=unix:/tmp/mininet-$1/db.sock --no-wait init

counter=0
while sleep 1;
do
  echo $counter >> /tmp/cpu_log;
  top -b -n 1 | egrep -i '%Cpu|ovs-vswitchd|:s1|:s2' | egrep -v 'grep' >> /tmp/cpu_log;
  ((counter++))
done

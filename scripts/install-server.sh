#!/bin/bash
#-----------------------
# add new instance
python $KAS_ADMIN --add-instance
# the instance will be pending, get its hostname
python $KAS_ADMIN --list | grep "pending" | awk '{if($3=="running") print $4}' > /tmp/ec2.pending
echo new server was added, hostname as follows
cat /tmp/ec2.pending


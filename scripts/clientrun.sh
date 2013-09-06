#!/bin/bash
KASDIR=`dirname $0`
source $KASDIR/../config/ec2rc
source $KASDIR/../config/setenv

if [ "$1" == "real" ]
then
  echo Step 1. running client A for 1 hour
  httperf --server $KAS_IP --port $KAS_PORT --num-conn 3600 --uri /work --period=d1 --hog &
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 2. running client B for 20 minutes
  httperf --server $KAS_IP --port $KAS_PORT --num-conn 1200 --uri /work --period=d1 --hog &
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 3. running client C for 25 minutes
  httperf --server $KAS_IP --port $KAS_PORT --num-conn 1700 --uri /work --period=d1 --hog &
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 4. running client D for 5 minutes
  httperf --server $KAS_IP --port $KAS_PORT --num-conn 300 --uri /work --period=d1 --hog &
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 5. Client D finished
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 6. Client B finished, the second instance should shut down
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 7. No changes
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 8. Client C finished.
  ps -Af | grep httperf
  $KASDIR/admin.sh -l
  sleep 5m
  echo Step 9. Client A finished.
  sleep 5m
  ps -Af | grep httperf
  echo End of test
  $KASDIR/admin.sh -l
else
  httperf --server $KAS_IP --port $KAS_PORT --num-conn 700 --uri /work --period=d1 --hog &
fi

#!/bin/bash
echo Bootstraping for a server
KASDIR=`dirname $0`
source $KASDIR/../config/ec2rc
source $KASDIR/../config/setenv

HOST=$1

echo This will install and run setup.sh on host $1
read -p "Are you sure?" yn

if [ "$yn" != "y" ]
then
  exit;
fi

# install the boot strap
echo Copying setup.sh...
scp -i config/$KAS_KEY.pem scripts/setup.sh ubuntu@$HOST:setup.sh
# run the boot strap
echo Running setup.sh...
ssh -i config/$KAS_KEY.pem ubuntu@$HOST ./setup.sh $2


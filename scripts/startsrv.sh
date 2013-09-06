#!/bin/bash
KASDIR=`dirname $0`
source $KASDIR/../config/ec2rc
source $KASDIR/../config/setenv
python $KAS_SERVER $*

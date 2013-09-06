#!/bin/bash
HOST=$1

source config/ec2rc
source config/setenv

ssh -i config/$KAS_KEY.pem ubuntu@$HOST
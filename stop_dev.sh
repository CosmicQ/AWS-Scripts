#!/bin/bash

# Script to stop instances belonging to certain groups.  Good for
# saving money overnight.

if [ ! $1 ]; then
  echo "Error:  You must specify group (developers|ops)"
  exit 1
fi

RUNNING=`aws ec2 describe-instances --filters Name=tag:Environment,Values=dev  Name=tag:Group,Values=$1 Name=instance-state-code,Values=16|grep INSTANCES|awk '{print $8}' |xargs`

NUM=`echo $RUNNING | wc -w`

if [ "$NUM" -ne "0" ]; then
  aws ec2 stop-instances --instance-ids $RUNNING
fi

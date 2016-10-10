#!/bin/bash
#
# Script to start a NAT host in AWS
# This was made before the NAT service was offered
#

# Start the instance and capture the instance ID (text default)

INSTANCEID=`aws ec2 run-instances --image-id ami-b0210ed8 --count 1 --instance-type t2.micro --key-name DEV --security-group-ids sg-b19585d6 --subnet-id subnet-5bc79870 --associate-public-ip-address --iam-instance-profile Arn=arn:aws:iam::123456789012:instance-profile/EC2BasicFunctions |grep INSTANCES |awk '{print $7}'`

# Add tags to the instance
aws ec2 create-tags --resources $INSTANCEID --tags "Key=Name,Value=nat" "Key=Environment,Value=dev" "Key=Function,Value=NAT" "Key=Group,Value=developers"

# Disable source dest check
aws ec2 modify-instance-attribute --instance-id $INSTANCEID --source-dest-check "{\"Value\": false}"

# The status of the instance must be "running" before we can update the route
STATUS=`aws ec2 describe-instances --instance-id $INSTANCEID |grep STATE|grep -v STATEREASON|awk '{print $3}'|xargs`

until [ "${STATUS}" == 'running' ]
do
  sleep 5
  STATUS=`aws ec2 describe-instances --instance-id $INSTANCEID |grep STATE|grep -v STATEREASON|awk '{print $3}'|xargs`
done

# Update the default route for the private subnets
aws ec2 replace-route --route-table-id rtb-7aac141e --destination-cidr-block 0.0.0.0/0 --instance-id $INSTANCEID


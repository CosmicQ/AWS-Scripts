#!/bin/bash
#
# To assume a role on the command line you need to export environment variables.
# Here is a quick command that generates output for you to cut-and-paste into
# the command line
#
# This assumes that you have awscli configured and that you have a valid role to assume
#
#export AWS_ACCESS_KEY_ID=""
#export AWS_SECRET_ACCESS_KEY=""
#export AWS_SECURITY_TOKEN=""

aws sts assume-role --role-arn arn:aws:iam::123456789012:role/Deployment --role-session-name "Production" --profile development |jq '.Credentials | "export AWS_ACCESS_KEY_ID=" + .AccessKeyId, "export AWS_SECRET_ACCESS_KEY=" + .SecretAccessKey, "export AWS_SECURITY_TOKEN=" + .SessionToken' | sed -e 's/^"//'  -e 's/"$//'

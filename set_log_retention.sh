#!/bin/bash
#
# Simple script to set the log retention in cloudwatch to other
# than "forever".  The first part is to collect the tokens for paging
# through the lists of logs.  Once we have that, we can update each
# log to expire at a reasonable date.
#
################################################
PROFILE=""
RETENTION="90"
LAMBDA="14"
APIGATE="30"
################################################

if [ -n "$1" ]; then
    PROFILE="--profile $1"
fi

REGIONS=("--region us-east-1" \
         "--region us-west-1" \
         "--region us-west-2" \
         "--region eu-west-1" \
         "--region eu-central-1" \
         "--region ap-south-1" \
         "--region ap-southeast-1" \
         "--region ap-northeast-1" \
         "--region ap-southeast-2" \
         "--region ap-northeast-2" \
         "--region sa-east-1")

NT=""
TOKENS=()
TOKENS[0]=" "

echo "Collecting tokens..."

for AWSREGION in "${REGIONS[@]}"; do

    while true; do
            RESULT=`aws $PROFILE $AWSREGION logs describe-log-groups $NT |jq .nextToken | sed -e 's/^"//'  -e 's/"$//'`
        if [ "$RESULT" = "null" ]; then
            # The last page has been found.  End this.
            break
        else
            TOKENS=("${TOKENS[@]}" "--next-token $RESULT")
            NT="--next-token $RESULT"
            echo "Adding $RESULT."
        fi
    done

    REGION_NAME=`echo $AWSREGION |awk '{print $2}'`
    echo "Setting retention policy on log groups in region $REGION_NAME..."

    for TOKEN in "${TOKENS[@]}"; do
        for LGN in `aws $PROFILE $AWSREGION logs describe-log-groups $TOKEN |jq '.logGroups[].logGroupName' | sed -e 's/^"//'  -e 's/"$//'`; do
            if [[ $LGN == *"lambda"* ]]; then
                aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $LAMBDA 
                echo "aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $LAMBDA"

            elif [[ $LGN == *"API-Gateway"* ]]; then
                aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $APIGATE 
                echo "aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $APIGATE"

            else
                aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $RETENTION 
                echo "aws $PROFILE $AWSREGION logs put-retention-policy --log-group-name $LGN --retention-in-days $RETENTION"

            fi
        done
    done

done

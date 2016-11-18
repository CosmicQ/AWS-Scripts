# AWS-Scripts/DynamoDB-Backups

_**generate-dynamodb-backup-template.py** - Interactive python 2.7 script for generating
a clouformation template, that creates a data pipeline used for backing up
dynamodb tables._

Requirements:
   * python 2.7
   * boto3
   * awscli installed and configured

# Operation

  Before running the script, make sure that awscli is configured with an account that has permissions
to read DynamoDB tables, and S3 buckets. DynamoDB is region specific, so you'll need to set the region you
want to make selections from before running the script.

TODO: Add region selection

  **generate-dynamodb-backup-template.py** is a menu driven script that allows the user to select
the DynamoDB tables to backup, the S3 buckets to store the backups in, and what bucket prefixes to use
if any prefixes are desired (s3 bucket subdirectories).

## DynamoDB Table Selection

  When selecting tables to backup, you mark one table at a time.  Selected tables are marked with an asterisk.
Once you have selected all the tables you wish to backup, press **x** to continue on to the destination
selection

## Destination S3 Bucket Selection

  Select the S3 bucket you wish to use to store your backups.  The S3 bucket must already exist in order to
select it.  You can only select one bucket to store backups in.  When you made your choice, press **x** to
continue

TODO: Add option to create the bucket

## Add prefixes

  You can group table backups into "subdirectories" by using prefixes.  Select the tables you wish to group,
and press **x** to continue.

## JSON file

  At this point, a cloudformation template will be created in the same directory the script is in called
"**dynamodb_backups.json**". This will create a datapipline that will do daily backups of the DynamoDB
tables.

#!/usr/bin/python
#
# Python script to generate a Cloudformation template to bakup specific DynamoDB tables.
# 

import boto3
import os
import time
import json

###################################################
#
# Functions
#
def collect_regions():
	# List S3 buckets
	print " Collecting regions..."
	client = boto3.client('ec2')
	region_list = [region['RegionName'] for region in client.describe_regions()['Regions']]

	region_list = sorted(region_list)
	table = dict()
	count = 1
	for elem in region_list:
		table[count] = dict()
		table[count]['select']    = False
		table[count]['name']      = elem
	
		count += 1
	return table
def collect_tables(region):
	# Fucntion to gather table names 
	print "\n\n Collecting DynamoDB table details..."
	client = boto3.client('dynamodb', region_name=region)
	dyn_list = client.list_tables()

	table = dict()
	count = 1
	for elem in dyn_list['TableNames']:
		details = client.describe_table(TableName=elem)
		table[count] = dict()

		table[count]['select']    = False
		table[count]['name']      = details['Table']['TableName']
		table[count]['status']    = details['Table']['TableStatus']
		table[count]['readUnits'] = details['Table']['ProvisionedThroughput']['ReadCapacityUnits']
		table[count]['size']      = details['Table']['TableSizeBytes']

		count += 1
	return table

def collect_buckets(region):
	# List S3 buckets
	print " Collecting S3 bucket names..."
	client = boto3.client('s3')
	bucket_list = client.list_buckets()

	table = dict()
	count = 1
	for elem in bucket_list['Buckets']:
		table[count] = dict()
		table[count]['select']    = False
		table[count]['name']      = elem['Name']

		count += 1
	return table

def dyn_menu(table, error):
	# Function to print the menu
	os.system('clear')
	my_session = boto3.session.Session()
	my_region = my_session.region_name
	print ("         Select tables to backup                          Region: %s " % my_region)
	print " "
	print "   {0:35} ({1:6})  {2:>15}          {3:>8}".format("Name", "Status", "Table Size", "Read Units")
	print "============================================================================================="

	for key, value in table.items():
		selected = ""
		if value['select'] == True:
			selected = "*"
		print "{0:1}  {1:2} {2:35} ({3:6})  {4:>15} bytes  {5:>8} read units".format(selected, key, value['name'], value['status'], value['size'], value['readUnits'])

	print " "
	if error == "error":
		print "    Invalid input."
	entered_data = raw_input('    Select the tables to backup by entering the number and pressing Enter.\nEnter \'x\' when done: ')


        dyntable = table
	return entered_data

def s3_menu(table, error):
	# Function to print the menu
	os.system('clear')
	print "         Select bucket for backup destination"
	print " "
	print "   {0:35}".format("Name")
	print "============================================================================================="

	for key, value in table.items():
		selected = ""
		if value['select'] == True:
			selected = "*"
		print "{0:1}  {1:2} {2:35}".format(selected, key, value['name'])

	print " "
	if error == "error":
		print "    Invalid input."
	entered_data = raw_input('    Select the S3 backup destination by entering the number and pressing Enter.\nEnter \'x\' when done: ')


        s3table = table
	return entered_data


def dyn_update_selection(n, table):
	# Function to update selected items
	if table[n]['select'] == False:
		table[n]['select'] = True
	else:
		table[n]['select'] = False

	return table
	

def s3_update_selection(n, table):
	# Function to update selected items
	if table[n]['select'] == False:
		table[n]['select'] = True
		num = len(table)
		mycount = 1
		# We can only have one selection.  Turn off all others
		while mycount < num:
			if mycount != n:
				table[mycount]['select'] = False
			mycount += 1

	else:
		table[n]['select'] = False

	return table

def add_prefix(selections, error):
	# Function to print the menu for adding a prefix to the storage destination
	os.system('clear')
	print "         Select tables to add prefixes to"
	print " "
	print "   {0:35}        {1:25}{2:25} ".format("Table","Bucket","Prefix")
	print "============================================================================================="

	for key, value in selections.items():
                if value['prefix']:
	                print "{0:2} {1:35} s3://{2:>1}/{3:<1}/".format(key, value['dynamo_table'], value['bucket'], value['prefix'])
                else:
	                print "{0:2} {1:35} s3://{2:>1}/".format(key, value['dynamo_table'], value['bucket'])

	print " "
	if error == "error":
		print "    Invalid input."
	entered_data = raw_input('    Select the table you wish to add a prefix to and press Enter.\nEnter \'x\' when done: ')

	return entered_data

def get_prefix(selection):
	entered_data = raw_input('    Enter the prefix you wish to add: ')
	return entered_data

def region_menu(table, error):
	# Function to print the menu
	os.system('clear')
	print "         AWS Regions"
	print " "
	print "   {0:35}".format("Name")
	print "============================================================================================="

	for key, value in table.items():
		selected = ""
		if value['select'] == True:
			selected = "*"
		print "{0:1}  {1:2} {2:35}".format(selected, key, value['name'])

	print " "
	if error == "error":
		print "    Invalid input."
	entered_data = raw_input('    Select the region by entering the number and pressing Enter.\nEnter \'x\' when done: ')


        s3table = table
	return entered_data
def region_update_selection(n, table):
	# Function to update selected items
	if table[n]['select'] == False:
		table[n]['select'] = True
		num = len(table)
		mycount = 1
		# We can only have one selection.  Turn off all others
		while mycount < num:
			if mycount != n:
				table[mycount]['select'] = False
			mycount += 1

	else:
		table[n]['select'] = False

	return table

###################################################
#
# Magic
#
###################################################

# Select Region
os.system('clear')
region_table    = collect_regions()
status = None
error_code  = None
while True:
	status = region_menu(region_table, error_code)

	if status == 'x':
		break

	if status.isalpha():
		error_code = "error"
	elif int(status) in region_table:
		region_update_selection(int(status), region_table)
		error_code = None
	else:
		error_code = "error"

for value in region_table:
        if region_table[value]['select'] == True:
		my_region = region_table[value]['name']

# Collect info
os.system('clear')
s3table    = collect_buckets(my_region)
dyntable   = collect_tables(my_region)

# Get the list of tables to backup
status = None
error_code  = None
while True:
	status = dyn_menu(dyntable, error_code)

	if status == 'x':
		break

	if status.isalpha():
		error_code = "error"
	elif int(status) in dyntable:
		dyntable = dyn_update_selection(int(status), dyntable)
		error_code = None
	else:
		error_code = "error"
# put the selections into the selections array
selections = dict()
count = 1
for value in dyntable:
        if dyntable[value]['select'] == True:
                selections[count] = dict()
                print dyntable[value]['name']
                selections[count]['dynamo_table'] = dyntable[value]['name']
                count += 1


# Select the bucket to backup to
status = None
error_code  = None
while True:
	status = s3_menu(s3table, error_code)

	if status == 'x':
		break

	if status.isalpha():
		error_code = "error"
	elif int(status) in s3table:
		s3_update_selection(int(status), s3table)
		error_code = None
	else:
		error_code = "error"

for location in s3table:
        if s3table[location]['select'] == True:
                for value in selections:
                        selections[value]['bucket'] = s3table[location]['name']
                        selections[value]['prefix'] = ""

############################
#
# one more menu option to add prefixes to the s3 bucket locations
#
# Present a kind of final view, like "These tables going to these buckets"
#
status = None
error_code  = None
while True:
        status = add_prefix(selections, error_code)

	if status == 'x':
                break

	if status.isalpha():
		error_code = "error"
	elif int(status) in s3table:
		prefix = get_prefix(int(status))
                selections[int(status)]['prefix'] = prefix
		error_code = None
	else:
		error_code = "error"

############################
#
# Print the cloudformation template
#

target = open("dynamodb_backups.json", 'w')
target.truncate()

# Header
target.write("""
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "The AWS CloudFormation template for backing up DynamoDB",

  "Parameters": {

    "BackupSubnetId": {
      "Description"          : "EMR Subnet (Must be public)",
      "Type"                 : "AWS::EC2::Subnet::Id"
    }
  },

  "Outputs": {
    "dynamoBackupBucket": {
      "Description": "Bucket where DynamoDB backups are stored",
      "Value"      : "%s"
    }
  },

  "Resources": {
    "DynamoBackupPipeline": {
      "Type": "AWS::DataPipeline::Pipeline",
      "Properties": {
        "Name": "main-dynamo-backup",
        "Description": "Pipeline to backup DynamoDB tables data to S3",
        "Activate": "true",
        "PipelineObjects": [
""" % selections[1]['bucket'])

# S3 Bucket Destination

for item1 in selections:
	target.write("""
          {{
            "Id": "{2}S3BackupLocation",
            "Name": "{2}S3BackupLocation",
            "Fields": [
              {{
                "Key": "type",
                "StringValue": "S3DataNode"
              }},
              {{
                "Key": "directoryPath",
                "StringValue": "s3://{0}/{1}{2}/#{{format(@scheduledStartTime, 'YYYY-MM-dd-HH-mm-ss')}}"
              }}
            ]
          }},""".format(selections[item1]['bucket'], selections[item1]['prefix'], selections[item1]['dynamo_table']) )

for item2 in selections:
	target.write("""
          {{
            "Id": "{0}",
            "Name": "{0}",
            "Fields": [
              {{
                "Key": "tableName",
                "StringValue": "{0}"
              }},
              {{
                "Key": "type",
                "StringValue": "DynamoDBDataNode"
              }},
              {{
                "Key": "readThroughputPercent",
                "StringValue": "0.25"
              }}
            ]
          }},
	""".format(selections[item2]['dynamo_table']) )

for item3 in selections:
	target.write("""
          {{
            "Id": "{0}BackupActivity",
            "Name": "{0}BackupActivity",
            "Fields": [
              {{
                "Key": "resizeClusterBeforeRunning",
                "StringValue": "false"
              }},
              {{
                "Key": "type",
                "StringValue": "EmrActivity"
              }},
              {{
                "Key": "input",
                "RefValue": "{0}"
              }},
              {{
                "Key": "output",
                "RefValue": "{0}S3BackupLocation"
              }},
              {{
                "Key": "runsOn",
                "RefValue": "EmrClusterForBackup"
              }},
              {{
                "Key": "maximumRetries",
                "StringValue": "2"
              }},
              {{
                "Key": "step",
                "StringValue": {{ "Fn::Join" : [ "", [
      "s3://dynamodb-emr-",
      {{ "Ref": "AWS::Region" }},
      "/emr-ddb-storage-handler/2.1.0/emr-ddb-2.1.0.jar,org.apache.hadoop.dynamodb.tools.DynamoDbExport,",
      "#{{output.directoryPath}},#{{input.tableName}},#{{input.readThroughputPercent}}" ]]}}
              }}
            ]
          }},
	""".format(selections[item3]['dynamo_table']) )

# Footer
target.write("""
          {
            "Id": "DefaultSchedule",
            "Name": "RunOnce",
            "Fields": [
              {
                "Key": "startAt",
                "StringValue": "FIRST_ACTIVATION_DATE_TIME"
              },
              {
                "Key": "type",
                "StringValue": "Schedule"
              },
              {
                "Key": "period",
                "StringValue": "1 Day"
              }
            ]
          },
          {
            "Id": "Default",
            "Name": "Default",
            "Fields": [
              {
                "Key": "type",
                "StringValue": "Default"
              },
              {
                "Key": "scheduleType",
                "StringValue": "cron"
              },
              {
                "Key": "failureAndRerunMode",
                "StringValue": "CASCADE"
              },
              {
                "Key": "role",
                "StringValue": "DataPipelineDefaultRole"
              },
              {
                "Key": "resourceRole",
                "StringValue": "DataPipelineDefaultResourceRole"
              },
              {
                "Key": "schedule",
                "RefValue": "DefaultSchedule"
              }
            ]
          },
          {
            "Id": "EmrClusterForBackup",
            "Name": "EmrClusterForBackup",
            "Fields": [
              {
                "Key": "subnetId",
                "StringValue": { "Ref": "BackupSubnetId" }
              },
              {
                "Key": "bootstrapAction",
                "StringValue": { "Fn::Join" : [ "", [
			"s3://",
			{ "Ref": "AWS::Region" },
			".elasticmapreduce/bootstrap-actions/configure-hadoop, ",
			"--yarn-key-value,yarn.nodemanager.resource.memory-mb=11520,",
			"--yarn-key-value,yarn.scheduler.maximum-allocation-mb=11520,",
			"--yarn-key-value,yarn.scheduler.minimum-allocation-mb=1440,",
			"--yarn-key-value,yarn.app.mapreduce.am.resource.mb=2880,",
			"--mapred-key-value,mapreduce.map.memory.mb=5760,",
			"--mapred-key-value,mapreduce.map.java.opts=-Xmx4608M,",
			"--mapred-key-value,mapreduce.reduce.memory.mb=2880,",
			"--mapred-key-value,mapreduce.reduce.java.opts=-Xmx2304m,",
			"--mapred-key-value,mapreduce.map.speculative=false" ]]}
              },
              {
                "Key": "terminateAfter",
                "StringValue": "2 Hours"
              },
              {
                "Key": "amiVersion",
                "StringValue": "3.9.0"
              },
              {
                "Key": "masterInstanceType",
                "StringValue": "m1.medium"
              },
              {
                "Key": "coreInstanceType",
                "StringValue": "m1.medium"
              },
              {
                "Key": "coreInstanceCount",
                "StringValue": "1"
              },
              {
                "Key": "type",
                "StringValue": "EmrCluster"
              }
            ]
          }
        ]
      }
    }
  }
}
""")

target.close()

print "\nEOP\n"

#!/usr/bin/python

import boto3, sys, getopt

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"k:s:r",["key=","secret=","region="])
   except getopt.GetoptError:
      print 'test.py --key <key> --secret <secret> --region <region>'
      sys.exit(2)

   key = None
   secret = None
   region = None

   for opt, arg in opts:
      if opt in ("-k", "--key"):
         key = arg
      elif opt in ("-s", "--secret"):
         secret = arg
      elif opt in ("-r", "--region"):
         region = arg

   if all([key, secret, region]):
      session = boto3.session.Session(
         aws_access_key_id=key,
         aws_secret_access_key=secret,
         region_name=region
      )
      client = session.client('cloudwatch')
      response = client.describe_alarms(StateValue='ALARM')
      print len(response['MetricAlarms'])
      sys.exit()

   else:
      print 'test.py --key <key> --secret <secret> --region <region>'
      sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])

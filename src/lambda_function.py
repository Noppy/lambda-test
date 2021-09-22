

import json
#import os
#import time
import logging
#import boto3

# Import Bolt for Python (github.com/slackapi/bolt-python)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


logGroupName = "security-alaert"
logStreamName = "development"
  
def lambda_handler(event, context):

    #Get Session
    #client = boto3.client('logs')

    #Put Log Event
    #Sput_logs(client, logGroupName, logStreamName, "Received event:{0}".format( json.dumps(event)))

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

"""
def put_logs(client, group_name, stream_name_prefix, message):
    try:
        #Set Logs Event Data
        log_event = {
            'timestamp': int(time.time()) * 1000,
            'message': message
        }
        
        #Set Flags
        exist_log_stream = True
        sequence_token = None

        while True:
            break_loop = False
            try:
                if exist_log_stream == False:
                    #Create LogGroup
                    try:
                        client.create_log_group(logGroupName=group_name)
                    except client.exceptions.ResourceAlreadyExistsException:
                        pass
                    #Create LogStream
                    create_log_stream_response = client.create_log_stream(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix)
                    exist_log_stream = True
                if sequence_token is None:
                    put_log_events_response = client.put_log_events(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix,
                        logEvents = [log_event])
                else:
                    put_log_events_response = client.put_log_events(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix,
                        logEvents = [log_event],
                        sequenceToken = sequence_token)
                    break_loop = True

            except client.exceptions.ResourceNotFoundException as e:
                exist_log_stream = False
            except client.exceptions.DataAlreadyAcceptedException as e:
                sequence_token = e.response.get('expectedSequenceToken')
            except client.exceptions.InvalidSequenceTokenException as e:
                sequence_token = e.response.get('expectedSequenceToken')
            except Exception as e:
                print(e)
            
            if break_loop:
                break
    except Exception as e:
        print(e)
"""
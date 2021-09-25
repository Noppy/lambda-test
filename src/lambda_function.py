

import json
import os
import time
import datetime
import logging
import boto3

# Import Bolt for Python (github.com/slackapi/bolt-python)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


logGroupName = "security-alaert"
logStreamName = "development"
  
def lambda_handler(event, context):

    #----------------------------------------
    # Initialize
    #----------------------------------------
    #Set parameters from environment values
    if os.environ['DRY_RUN'].lower == "true":
        dry_run = True
    else:
        dry_run = False
    slack_token   = os.environ['SLACK_TOKEN'] 
    logGroupName  = os.environ['LOG_GROUP']
    logStreamName = datetime.datetime.now().strftime('%Y%m%d')

    #Get Session
    logs_client = boto3.client('logs')
    slack_client = WebClient( token=os.environ['SLACK_TOKEN'] )

    #----------------------------------------
    # Identify the channel to send
    #----------------------------------------

    #----------------------------------------
    # Send Message
    #----------------------------------------
    ret = slack_client.chat_postMessage(channel="for-test", text="Hello world")
    put_logs(logs_client, logGroupName, logStreamName, "Received event:{0}".format( json.dumps(event)))






    #Put Log Event
    

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


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
                    client.create_log_stream(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix)
                    exist_log_stream = True
                    #Write First event log
                    client.put_log_events(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix,
                        logEvents = [log_event])
                    break_loop = True
                elif sequence_token is None:
                    client.put_log_events(
                        logGroupName = group_name,
                        logStreamName = stream_name_prefix,
                        logEvents = [log_event])
                else:
                    client.put_log_events(
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

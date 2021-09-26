

import json
import os
import time
import datetime
import re
import logging
import boto3

# Import Bolt for Python (github.com/slackapi/bolt-python)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# shared accounts
shared_accounts_list = [
    "777777777777"
]

# Slack channel name
slack_channel_name_list = {
    "shared": "lv-shared-aws-secalerts",
    "other":  "lv-other-aws-secalerts"
}


# Set debug mode
if os.environ['DEBUG'].lower() != "true":
    DEBUG = False
else:
    DEBUG = True

# Set logging mode, log group and log stream
logger = logging.getLogger()
if DEBUG:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)

logGroupName  = os.environ['LOG_GROUP']
logStreamName = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9), 'JST')).strftime('%Y%m%d')


#----------------------------------------
# Main
#----------------------------------------
def lambda_handler(event, context):

    # Check if the event is a security hub finding
    logger.warning("{0}".format( json.dumps(event)))
    if event['source'] != 'aws.securityhub':
        logger.error('This event is not a SecurityHub event')
        return { 'statusCode': 400 }
    
    # Extract necessary information
    finding_info = get_securityhub_finding(event)
    logger.info(json.dumps(finding_info))

    # Get sessions
    session = {
        'logs':  boto3.client('logs'),
        'slack': WebClient( get_slack_token('aaa') )
    }

    # Identify the channel to send, and publish a message
    channel_name = detect_slack_channel(session, finding_info)
    publish_message(session, channel_name, finding_info)

    #success
    return { 'statusCode': 200 }

#----------------------------------------
# Functions
#----------------------------------------
# Extract necessary information
def get_securityhub_finding(event):
    finding = event['detail']['findings'][0]
    ret = {
        'detail-type':  event['detail-type'],
        'region':       finding['Region'],
        'AwsAccountId': finding['AwsAccountId'],
        'Title':        finding['Title'],
        'Description':  finding['Description'],
        'Types':        finding['FindingProviderFields']['Types'][0],
        'FirstSeen':    finding['FirstObservedAt'],
        'LastSeen':     finding['LastObservedAt'],
        'Resource':     finding['ProductFields']['Resources:0/Id'],
        'Severity':     finding['FindingProviderFields']['Severity']['Label']
    }
    return ret


# Get SLACK_TOKEN to Systems Manager parameter store
def get_slack_token(key=''):
    client = boto3.client('ssm')
    ret = client.get_paramet(
        Names = [ key ],
        WithDecryption = True
    )
    return ret['Parameters'][0]['Value']

# Identify the slack channel to send security alert.
def detect_slack_channel(session, finding_info):
    accountid = finding_info['AwsAccountId']

    #check shared accounts
    for i in shared_accounts_list:
        logger.info( "shared account check: finding's account: {} check account: {}".format(accountid, i) )
        if accountid == i:
            logger.warning( "shared account check: detect account: {}".format(i) )
            return slack_channel_name_list['shared']
    
    #check resource accounts
    channels = session['slack'].conversations_list(
        limit=1000,
        exclude_archived = True
    )
    for ch in channels['channels']:
        ch_name = ch['name']
        logger.info( "resource account check: finding's account: {} slack channel: {}".format(accountid, ch_name) )
        channel_awsid = "NA"
        match = re.search(r'.*([0-9]{12})$', ch_name)
        if match:
            channel_awsid = match.groups()[0]
            if accountid == channel_awsid:
                logger.warning( "resource account check: detect account: channel is {}".format(ch_name) )
                return ch_name

    #other accounts
    logger.warning( "not found slack channel: set the other channel({})".format(slack_channel_name_list['other']) )
    return slack_channel_name_list['other']


# Publish message to specifed slack channel and logs
# (In dry-run mode, write only to logs)
def publish_message(session, channel, finding):
    # Create message
    message = '*{}|{}|Account: {}*\n'.format( finding['detail-type'], finding['region'], finding['AwsAccountId'] ) + \
              '*{}*\n\n{}\n\nFinding Type: {}\n\n'.format( finding['Title'], finding['Description'], finding['Types']) + \
              'First Seen: `{}`\nLast Seen: `{}`\nAffected Resource: `{}`\nSeverity: `{}`'.format( finding['FirstSeen'], finding['LastSeen'], finding['Resource'], finding['Severity'] )

    # Publish message
    logger.warning("slack channel: {}\nmessage: {}".format(channel, message))
    put_logs(session['logs'], logGroupName, logStreamName, "slack channel: {}\nmessage: {}".format(channel, message))  
    if not DEBUG:
        try:
            session['slack'].chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            logger.error( e.response["error"] )
    return


# Write message to specifed log group
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
                logger.error(e)
            
            if break_loop:
                break
    except Exception as e:
        logger.error(e)

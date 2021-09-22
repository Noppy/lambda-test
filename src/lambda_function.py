

import os
import json
import logging

# Import Bolt for Python (github.com/slackapi/bolt-python)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):



    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
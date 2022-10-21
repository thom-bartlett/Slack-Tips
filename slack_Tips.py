#!/usr/bin/env python3
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from slack_sdk import WebClient
import os
import logging
import sys

logging.basicConfig(filename='slack-tip.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s' - '%(asctime)s')


# dependencies
# GOOGLE_APPLICATION_CREDENTIALS env variable - export GOOGLE_APPLICATION_CREDENTIALS="/Users/tbartlett/Downloads/slack-tips-346919-90d0c65439ba.json"
# SLACK_BOT_TOKEN env variable - 
# Slack SDK
# Google SDK

# to do
if len(sys.argv) > 1:
    mode = str(sys.argv[1])
else:
    mode = "prod"

logger = logging.getLogger(__name__)
creds, _ = google.auth.default()
service = build('sheets', 'v4', credentials=creds)
spreadsheet = "111WG0e8enyzPOeh0jb0cKNQMa9DtT4CMRgwAoX6cIjk"
logging.info('Got initial data')

def get_values(spreadsheet_id, range_name):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.\n"
        """
    # pylint: disable=maybe-no-member
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name, valueRenderOption="FORMULA").execute()
        index = int((result["values"][1][1]))
        tip = result["values"][index][0]
        logger.info(f"Tip retrieved: {tip}")
        total_Rows = len(result["values"])
        if mode != "test":
            if index == total_Rows - 1:
                index = 0
            else:
                index += 1
        logging.info('Retrieved tip from spreadsheet')
        return index, tip
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return error

def post_Value(value_input_option, index):
    values = [
        [
            index
        ],
    # Additional rows ...
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet, range="B2:B2",
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
    logging.info('Index updated')

def notify(tip):
    # Message the user
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(bot_token)
    blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Tuesday Tech Tips",
                    }
                },
                {
                    "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{tip}"
                        },
                }
    ]
    logging.info('Tip sent to channel')

    try:
        if mode == "test":
            client.chat_postMessage(channel="C032RQVRNS3", blocks=blocks)
            logger.info("Tip Sent")
        else:
            client.chat_postMessage(channel="C57CR4WCT", blocks=blocks)
            logger.info("Tip Sent")
    except Exception as e:
        logger.exception(f"Failed to post a message error: {e}")

pull = get_values(spreadsheet, "A1:B100")
post_Value("USER_ENTERED", pull[0])
notify(pull[1])
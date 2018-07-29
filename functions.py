import requests
import logging
import re
import time
import csv

#start the logging module
logger = logging.getLogger(__name__)


def discordapi_check_channel_access(channel, header):
    request = requests.get("https://discordapp.com/api/channels/"+channel+"/messages?limit=1", headers=header)
    if request.status_code == 200:
        return True
    else:
        logger.error(request.status_code)
        return False

def discordapi_get_messages_batch(channel, before, header):
    request = requests.get("https://discordapp.com/api/channels/"+channel+"/messages?limit=100&before="+before, headers=header)
    if request.status_code == 200:
        return request.json()
    else:
        logger.warn("DISCORD API PROBLEM! - Got status code {}. Waiting 10 seconds".format(request.status_code))
        time.sleep(10)
        return False

def discordapi_delete_message(channel, message, header):
    request = requests.delete("https://discordapp.com/api/channels/"+channel+"/messages/"+message, headers=header)
    if request.status_code == 204:
        return True
    elif request.status_code == 429:
        json = request.json()
        wait_timer = round(float(json['retry_after'] / 1000) + 1, 3)
        logger.warn("DISCORD API RATE LIMIT! - Backing off and retrying in {} seconds".format(wait_timer))
        time.sleep(wait_timer)
        return False
    else:
        logger.error("DISCORD API UNKNOWN ERROR! Status code {}".format(request.status_code))
        return False

#return True if we should delete the message
def message_parser_user(message, users):
    if message['author']['id'] in users:
        return message['author']['id']
    else:
        return False

#return True if we should delete the message
def message_parser_regex(message, regex):
    regex_found = re.findall(regex, message['content'].lower())
    if len(regex_found) == 0:
        return False
    else:
        return regex_found

def archive_message_csv(channel, message, file):
    with open(file, 'a', encoding='utf-8', newline='') as f:
        f_writer = csv.writer(f)
        f_writer.writerow([message['timestamp'], channel['id'], channel['name'], message['id'], message['author']['id'], message['author']['username'], message['content']])
    return True

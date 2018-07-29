import requests
import time
import argparse
import json
import logging

from functions import *

#start the logging module
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#load the configuration file
try:
	with open("config.json", "r") as cfgFile:
		cfg = json.load(cfgFile)
except Exception as e:
	logger.critical("Unable to start script (something with config.json is wrong?). Error:{}".format(e))
	exit()

#load in optional arguements to resume, to prevent re-iteration over millions of messages
arg = argparse.ArgumentParser()
arg.add_argument("-rf", "--resumefrom")
arg.add_argument("-rc", "--resumechannel")
args = vars(arg.parse_args())

#build the discord headers
discord_headers = {'Authorization':'Bot '+cfg['token']}

#get all the server channels
channels_req = requests.get("https://discordapp.com/api/guilds/"+cfg['guild']+"/channels", headers=discord_headers)
if channels_req.status_code != 200:
	logger.critical("Invalid Discord Guild! (check your token and bot permissions?)")
	exit()
else:
	channels_raw = channels_req.json()

#if the --resumechannel flag is set, lets skip to that channel
if args['resumechannel']:
	i=0
	for channel in channels_raw:
		if channel['id'] != str(args['resumechannel']):
			logger.info("RESUME: Skipping '{0[id]}' (#{0[name]}) on loop '{1}'".format(channel, i))
		else:
			logger.info("RESUME: Resuming on '{0[id]}' (#{0[name]}) on loop '{1}'".format(channel, i))
			break
		i+=1
	channels = channels_raw[i:]
else:
	channels = channels_raw

#run through the channels, yes this is nested pretty badly don't @ me
for channel in channels:
	if channel['type'] == 0:
		if discordapi_check_channel_access(channel['id'], discord_headers):
			print("ALLOWED CHANNEL READ", channel['id'], channel['name'])

			if args['resumefrom'] and args['resumechannel'] == channel['id']:
				BEFORE = args['resumefrom']
			else:
				BEFORE = channel['last_message_id']

			while True:
				logger.info("GETTING BATCH OF 100 MESSAGES: LAST ID {} in {}".format(BEFORE, channel['name']))
				msgs = discordapi_get_messages_batch(channel['id'], BEFORE, discord_headers)

				for msg in msgs:
					LASTID = msg['id']

					if cfg['mode'].lower() == "users":
						message_result = message_parser_user(msg, cfg['match_users'])
					elif cfg['mode'].lower() == "regex":
						message_result = message_parser_regex(msg, cfg['match_regex'])
					else:
						logger.critical("Unsupported mode! (should be set to either users or regex)")
						exit()

					#if this is returned to be true from the parsers, we have to act on the message
					if message_result:
						logger.info("MSG FOUND: Reason: {} Message: {}".format(message_result, msg['content'].lower()))

						delet = discordapi_delete_message(channel['id'], msg['id'], discord_headers)
						while delet is not True:
							delet = discordapi_delete_message(channel['id'], msg['id'], discord_headers)

						if cfg['archival_enabled']:
							archive_message_csv(channel, msg, cfg['archival_file'])

				#if the LASTID is not changing, we hit the end of the channel
				if BEFORE == LASTID:
					break
				else:
					BEFORE = LASTID

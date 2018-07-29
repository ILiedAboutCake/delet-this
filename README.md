# Delet This
#### Purge your Discord server of unwanted previous messages by regex or account IDs

Discord makes it difficult to truely remove data from the platform. Using this script you can scrub your entire server back to the first messages at creation using 2 different matching patterns:

1. Regex based deletion on the message contents
2. Message deletion based on the creators user ID

It is highly recommended setting your Discord [client to developer mode](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
and having a basic understanding of the [Discord snowflake ID format](https://discordapp.com/developers/docs/reference#snowflakes) before attempting to use this script.

**Per the Discord TOS this script is designed to only accept valid [Bot tokens](https://discordapp.com/developers/applications/) and respects enforced rate limits.
Running userbots will get your account disabled and is NOT recommended.**

## Example config.json
```Json
{
    "guild":"265256381437706240",
    "token":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "mode":"regex",
    "match_regex":"\\bretard(?:ed)?\\b",
    "match_users":["252869311545212928","265255911012958208"],
    "ignore_channels":["270579644372090880","356781927836942339","270578632026488851","270695480873189376","419976078321385473","273164941857652737"],
    "archival_enabled":"true",
    "archival_file":"deleted_this.csv"
}

```

| Setting | Accepted Value |
|---------|----------------|
| guild   | Discord Server Snowflake |
| token   | Discord Bot Token |
| mode    | "regex" or "users" |
| match_regex | regex to compare messages against if mode is set to regex |
| match_users | list of Discord User Snowflakes if mode is set to users |
| ignore_channels | list of Discord Channel Snowflakes to bypass, can be empty list |
| archival_enabled | true or false, toggles saving of deleted messages |
| archival_file | location to save deleted messages csv if archival_enabled is true |

## Command Line Parameters

These are optional. Best used to pick off where the script stopped on a crash or disconnect.

```
--resumefrom <Discord Message Snowflake>
--resumechannel <Discord Channel Snowflake>
```

## Running delet.py
```
python .\delet.py
python .\delet.py --resumechannel 265256381437706240
python .\delet.py --resumechannel 265256381437706240 --resumefrom 469620983704190999
```

## Notes

This is written in Python 3, with the only external library needed is Requests. This can be done with `python3 -m pip install -r requirements.txt`.

Depending on your server message volume size and messages to be deleted this might take several days to run. My testing revealed a rate of about 1000 messages per hour can be deleted from the API.

The bot account you are running this under must have the `VIEW_CHANNEL`, `READ_MESSAGE_HISTORY`, and `MANAGE_CHANNELS` permissions in all channels you wish to scrub

# HBD Bot

A Telegram bot that reads birthday dates from a Google Spreadsheet and posts a message to a Telegram group in case it's someone's birthday. Sweet!

## How to
Provide your settings through _config.json_ file:
- api_token: your Telegram bot API token
- cache_file: file to store data last read from a spreadsheet. Default: _.hbdcache_
- sheet_id: ID of your Spreadsheet taken from the URL: https://docs.google.com/spreadsheets/d/**1ZeNzpGJr4ouXqg_AoyA7WYuMP3exgMBvr8QE85M081Q**/edit#gid=0
- sheet_name: name of the sheet with data (see below for expected format)
- chat_name: name of Telegram group to post messages to, as @telegramgroup
- report_name: name of Telegram group to post log messages to, as @telegramgroup
- log_file: path to local log file, default _hbdbot.log_

Expected data format:
| Date | Name | Telegram handle |
| ------ | ------ | ------ |
| 25.04 | Name (UTF-8) | @telegramhandle |

Run bot script via scheduler at any desired interval. Example for cron:
```sh
0 10 * * * python3 /hbdbot/hbd.py -C config.json &>/hbdbot/cron_job.log
```
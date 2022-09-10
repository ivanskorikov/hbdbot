import urllib.request
import urllib.parse
from datetime import datetime
import telebot
from json import load, dump
import argparse

class Config():
    config_file = 'config.json'

    def __init__ (self, config_file):
        self.config_file = config_file
        config = self.read_config_file(self.config_file)
        
        self.api_token = config['api_token']
        self.sheet_id = config['sheet_id']
        self.raw_sheet_name = config['sheet_name']
        self.sheet_name=  urllib.parse.quote(self.raw_sheet_name)
        self.cache_file = config['cache_file']
        self.chat_name = config['chat_name']
        self.report_name = config['report_name']
        self.log_file = config['log_file']
        self.sheet_url = f'https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}'     

    def read_config_file(self, cfg):
        with open(cfg, 'r', encoding='utf-8') as cfg_file:
            c = load(cfg_file)
            return c

def pad_date_string(date_string):
    return date_string.zfill(5)

def normalize_line(line):
    line = line.decode('utf-8').strip().replace('"', '').split(',')
    line[0] = pad_date_string(line[0])
    return line

def get_current_date():
    return datetime.today().strftime('%d.%m')

def report(msg, bot, dest):
    bot.send_message(dest, msg)

def read_birthdays_from_sheet(sheet_url):
    bdays = dict()
    try:
        request_result = urllib.request.urlopen(sheet_url)
        for line in request_result:
            dob, string_name, telegram_name = normalize_line(line)
            if dob in bdays:
                bdays[dob].append([string_name, telegram_name])
            else:
                bdays[dob] = [[string_name, telegram_name]]
    except Exception as e:
        bdays = None
    
    return bdays

def read_birthdays_from_cache(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as c:
        cached = load(c)
        return cached

def generate_message(persons):
    names = ''
    if len(persons) == 1:
        verb = 'отмечает'
    else:
        verb = 'отмечают'
    for p in persons:
        names = names + ' '.join(p) + ', '
    names = names.rstrip(', ')
    message = f'🎉🎉🎉🎉🎉🎉🎉🎉\nВсем привет\!\nСегодня день рождения {verb} *{names}*\! Поздравляем\!\n🎂🎂🎂🎂🎂🎂🎂🎂'
    return message

def check_today(today, bdays):
    if today in bdays:
        return generate_message(bdays[today])
    else:
        return False

def update_cache(cache, remote):
    with open(cache, 'w') as c:
        c.truncate()
        dump(remote, c, indent = 4)

def logger(msg, log):
    t = datetime.today().strftime('%c')
    with open(log, 'a', encoding='utf-8') as l:
        l.write(f'{t}\t{msg}\n')

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-C', '--config', type=str, nargs='?', default='./config.json', help='Path to json config file')
    args = argparser.parse_args()

    cfg = Config(config_file=args.config)
    bot = telebot.TeleBot(cfg.api_token)
    fetched_remote = False
    
    today = get_current_date()
    logger(f'==========8<==========', cfg.log_file)
    logger(f'Init complete. Using {cfg.config_file}. Got date: {today}', cfg.log_file)
    birthdays = read_birthdays_from_sheet(cfg.sheet_url)
    if birthdays:
        logger(f'Fetched remote data from {cfg.sheet_url}', cfg.log_file)
        congratz = check_today(today, birthdays)
        fetched_remote = True
    else:
        logger(f'Using local cache at {cfg.cache_file}', cfg.log_file)
        birthdays = read_birthdays_from_cache(cfg.cache_file)
        congratz = check_today(today, birthdays)

    if congratz:
        bot.send_message(cfg.chat_name, congratz, parse_mode='MarkdownV2') 
        logger(f'HBD message sent to {cfg.chat_name}', cfg.log_file)     
    else:
        logger(f'Nothing to send.', cfg.log_file)     

    if fetched_remote: 
        update_cache(cfg.cache_file, birthdays)
        logger(f'Local cache updated at {cfg.cache_file}', cfg.log_file)
    
    report(f'Success!\nToday: {today}.\nUpdated cache: {str(fetched_remote)}', bot, cfg.report_name)
    
if __name__ == '__main__':
    main()
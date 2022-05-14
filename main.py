import telegram
import feedparser
import psycopg2
from time import sleep
import datetime
import sys
import json


def format_fancy_message(new_item):
    annotation = new_item['summary']
    annotation = annotation.replace('</p>', '')
    annotation = annotation.replace('<p>', '')
    annotation = annotation.replace('\n', '')
    good_message = '<b>' + new_item['title'] + '</b>' + '\n' + new_item['link'] + '\n<pre>\n' + annotation + '</pre>\n'
    print(good_message)
    return good_message


def insert_upd_in_registered_chats(upd, conn):
    now = datetime.datetime.now()
    cursor = conn.cursor()
    query = f"INSERT INTO registered_chats VALUES({upd['message']['chat']['id']}, " \
            f"'{upd['effective_user']['username']}', '{now}') ON CONFLICT DO NOTHING"
    print(query)
    cursor.execute(query)
    conn.commit()


def choose_chat_ids(conn):
    cursor = conn.cursor()
    query = 'SELECT chat_id FROM registered_chats'
    cursor.execute(query)
    list_chat_ids = []
    for s in cursor.fetchall():
        list_chat_ids.append(s[0])
    return list_chat_ids


config_file = open('config.json', 'r')
config_data = config_file.read()
config = json.loads(config_data)
conn = psycopg2.connect(**config['connection'])  # распаковываем второй вложенный словарь в json по ключам

bot = telegram.Bot(token=config['bot_token'])
chat_ids = set()
arxiv_cs_ds_url = 'http://arxiv.org/rss/cs.DS'
sent = set()


while True:
    print('new_iteration')
    # new incoming message in the bot
    updates = bot.get_updates(read_latency = 10)
    feed = feedparser.parse(arxiv_cs_ds_url)

    new_item = None
    for item in feed['items']:
        if item['link'] not in sent:
            new_item = item
            break

    if new_item is None:
        sleep(60)
        continue

    # gathering chat ids for incoming messages
    for upd in updates:
        chat_ids.add(upd['message']['chat']['id'])
        if '/start' in upd['message']['text']:
            print('start found')
            insert_upd_in_registered_chats(upd, conn)

    for chat_id in choose_chat_ids(conn):
        bot.send_message(text=format_fancy_message(new_item),
                         chat_id=chat_id, parse_mode=telegram.constants.PARSEMODE_HTML)
    sent.add(new_item['link'])

import telegram
import feedparser
from time import sleep


def format_fancy_message(new_item):
    annotation = new_item['summary']
    annotation = annotation.replace('</p>', '')
    annotation = annotation.replace('<p>', '')
    annotation = annotation.replace('\n', '')
    good_message = '<b>' + new_item['title'] + '</b>' + '\n' + new_item['link'] + '\n<pre>\n' + annotation + '</pre>\n'
    print(good_message)
    return good_message


bot = telegram.Bot(token='5299733983:AAHHkZK3kHq0psPqlovDNDlDxsG4Bn0bDnY')
chat_ids = set()
arxiv_cs_ds_url = 'http://arxiv.org/rss/cs.DS'
sent = set()

while True:
    # new incoming message in the bot
    updates = bot.get_updates()
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
    for chat_id in chat_ids:
        bot.send_message(text=format_fancy_message(new_item),
                         chat_id=chat_id, parse_mode=telegram.constants.PARSEMODE_HTML)
    sent.add(new_item['link'])
    print(chat_ids)

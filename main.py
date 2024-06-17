import flask
import telebot
import os
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pymorphy2 import MorphAnalyzer
from utils import lemmatizer, colloc, parse_glossary, parse_glossary_trash, clear_search, trash_search, compile_response, search

TOKEN = "7478481379:AAHmQqU00naXttUJGmqoXA_AdAtinyTNLkI"

print("START PARSING TSV FILE")
glossary, output_terms = parse_glossary('glossary.tsv')
glossary_t, output_terms = parse_glossary_trash('glossary.tsv', output_terms)
print("FINISH PARSING TSV FILE, STARTING TELEGRAM BOT")

bot = telebot.TeleBot(TOKEN, threaded=False)

app = flask.Flask(__name__)

@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'

@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

@app.route("/set_webhook", methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url="https://your_pythonanywhere_username.pythonanywhere.com/bot")
    return 'Webhook set successfully'

@app.route("/remove_webhook", methods=['GET'])
def remove_webhook():
    bot.remove_webhook()
    return 'Webhook removed successfully'

if __name__ == '__main__':
    app.run()

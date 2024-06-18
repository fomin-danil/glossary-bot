import flask
import telebot
import os
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pymorphy2 import MorphAnalyzer
from utils import lemmatizer, colloc, parse_glossary, parse_glossary_trash,\
     clear_search, trash_search, compile_response, search

TOKEN = os.environ["TOKEN"]

print("START PARSING TSV FILE")
glossary, output_terms = parse_glossary('glossary.tsv')
glossary_t, output_terms = parse_glossary_trash('glossary.tsv', output_terms)
print("FINISH PARSING TSV FILE, STARTING TELEGRAM BOT")

bot = telebot.TeleBot(TOKEN, threaded=False)


bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://pythoneduson.herokuapp.com/bot")

app = flask.Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    current_message_id = message.message_id
    message_replied = []
    if current_message_id not in message_replied:
        message_replied.append(current_message_id)
        bot.send_message(message.chat.id, "Здравствуйте! Это бот-глоссарий, у которого можно узнать, что значат термины. Напишите, что бы вы хотели узнать.")



@bot.message_handler(func=lambda m: True)  # этот обработчик реагирует все прочие сообщения
def send_response(message):
    print('Receieved a message!')
    current_message_id = message.message_id
    message_replied = []
    global glossary, glossary_t, output_terms
    message_text = str(message)
    output = lemmatizer(message_text)
    words, bigramms = colloc(output)
    final_result = search(words, bigramms, glossary, output_terms, glossary_t)
    m = final_result
    if len(m) > 4095:
        for x in range(0, len(m), 4095):
            bot.send_message(message.chat.id, text=m[x:x+4095])
    if current_message_id not in message_replied:
        message_replied.append(current_message_id)
        bot.send_message(message.chat.id, text=m)
        print('Processed a message!')



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
    
if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

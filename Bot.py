import traceback
import telebot
from telebot import types
import datetime
import time
from multiprocessing import Process
from Dialogues import Dialogues
from Callbacks import Callbacks
import Texts
from DataBase import DataBase


TOKEN = ""

bot = telebot.TeleBot(TOKEN)


dialogues_by_id = {}
callbacks_by_id = {}
dict_callbacks_by_id = {}
database = DataBase()


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    user_id = message.from_user.id
    dialogues = Dialogues(bot, database, user_id)
    callbacks = Callbacks(bot, dialogues)
    dialogues_by_id[user_id] = dialogues
    callbacks_by_id[user_id] = callbacks
    dialogues_by_id[user_id].first_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    try:
        callbacks_by_id[call.from_user.id].main_callback(call)
    except Exception as e:
        bot.send_message(call.from_user.id, Texts.idle_msg)
        print(e)
        Bot.log_exception(e)


class Bot:
    def __init__(self):
        pass

    def run(self):
        while True:
            try:
                print("Bot is running")
                database.curs.reset()
                bot.polling(none_stop=True, interval=0)
            except Exception as e:
                print(e)
                Bot.log_exception(e)

    def log_exception(e: Exception):
        with open("Logs/error_logs.txt", "a") as log_file:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(time + "\n")
            log_file.write(str(e) + "\n")
            log_file.write(traceback.format_exc() + "\n\n")

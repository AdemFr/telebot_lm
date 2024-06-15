import logging
import os

import telebot

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(os.environ["TOKEN"])


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

import logging
import os

import ollama
import telebot

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(os.environ["TOKEN"])

bot.set_chat_menu_button()


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    stream = ollama.chat(
        model="phi3:mini",
        messages=[{"role": "user", "content": message.text}],
        stream=True,
    )

    output = ""
    for chunk in stream:
        _output = chunk["message"]["content"]
        output += _output
        print(_output, end="", flush=True)
        if chunk["done"]:
            print("")
    bot.reply_to(message, output)

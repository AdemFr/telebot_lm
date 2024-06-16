import logging
import os

import ollama
import telebot

from telebot_lm.ollama_runner import OllamaRunner

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(os.environ["TOKEN"])

bot.set_chat_menu_button()
runner = OllamaRunner()


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Starting to answer your question...")
    message.text
    stream = ollama.chat(
        model=runner.model,
        messages=[{"role": "user", "content": message.text}],
        stream=True,
    )

    logger.info("Start generating...")
    output = ""
    for chunk in stream:
        _output = chunk["message"]["content"]
        output += _output
        print(_output, end="", flush=True)
        if chunk["done"]:
            print("")
    logger.info(f"Generated output for message: {output}")
    bot.reply_to(message, output)

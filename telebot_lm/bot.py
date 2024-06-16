import logging
import os

import telebot
from telebot import types

from telebot_lm.gcp_handler import GCPInstanceHandler
from telebot_lm.ollama_runner import MODELS, OllamaRunner

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(os.environ["TOKEN"])

commands = [
    types.BotCommand(command="start_machine", description="Start remote VM"),
    types.BotCommand(command="stop_machine", description="Get help information"),
    types.BotCommand(command="machine_status", description="Get remote VM status"),
    types.BotCommand(command="start_ollama", description="Statup Ollama server"),
    types.BotCommand(command="stop_ollama", description="Stop Ollama server"),
    types.BotCommand(command="get_models", description="Get available models"),
]

bot.set_my_commands(commands)
bot.set_chat_menu_button()

gcp_handler = GCPInstanceHandler(
    project=os.environ["PROJECT_ID"],
    zone=os.environ["ZONE"],
    service_name=os.environ["SERVICE_NAME"],
)


@bot.message_handler(commands=["start_machine"])
def start_machine(message):
    result = gcp_handler.start_instance()
    bot.reply_to(message, result)


@bot.message_handler(commands=["stop_machine"])
def stop_machine(message):
    result = gcp_handler.stop_instance()
    bot.reply_to(message, result)


@bot.message_handler(commands=["machine_status"])
def get_staus(message: types.Message):
    result = gcp_handler.get_status()
    bot.reply_to(message, result)


@bot.message_handler(commands=["start_ollama"])
def start_ollama(message):
    if not os.environ.get("POLLING"):
        bot.reply_to(message, "Running as webhook, please start on VM bot.")
    OllamaRunner().start_ollama()
    bot.reply_to(message, "Ollama started")


@bot.message_handler(commands=["stop_ollama"])
def stop_ollama(message):
    OllamaRunner().stop_ollama()
    bot.reply_to(message, "Ollama stopped")


@bot.message_handler(commands=["get_models"])
def get_models(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text=model, callback_data=model)
        for model in MODELS.keys()
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Choose a model:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in MODELS.keys())
def handle_model_choice(call):
    model = call.data
    runner = OllamaRunner()
    if runner.process is None:
        bot.answer_callback_query(
            call.id, "Ollama is not running. Start it with /start_ollama"
        )
        return
    runner.set_model(model)
    bot.answer_callback_query(call.id, f"Model {model} set")


@bot.message_handler(func=lambda message: True)
def chat(message):
    runner = OllamaRunner()
    if runner.process is None:
        bot.reply_to(message, "Ollama is not running. Start it with /start_ollama")
        return

    agent_prompt = runner.agent_choice(message.text)
    response = runner.chat(agent_prompt + message.text)
    bot.reply_to(message, response)

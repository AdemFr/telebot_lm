import logging
import os
from functools import wraps

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
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", -1))
RESTRICTED_IDS = [ADMIN_CHAT_ID]


def restricted(func):
    @wraps(func)
    def wrapped(message: types.Message):
        user_id = message.chat.id
        if user_id not in RESTRICTED_IDS:
            bot.reply_to(message, "Not authorized.")
            return
        return func(message)

    return wrapped


@bot.message_handler(commands=["start_machine"])
@restricted
def start_machine(message: types.Message):
    result = gcp_handler.start_instance()
    bot.reply_to(message, result)


@bot.message_handler(commands=["stop_machine"])
@restricted
def stop_machine(message: types.Message):
    result = gcp_handler.stop_instance()
    bot.reply_to(message, result)


@bot.message_handler(commands=["machine_status"])
@restricted
def get_staus(message: types.Message):
    result = gcp_handler.get_status()
    bot.reply_to(message, result)


@bot.message_handler(commands=["start_ollama"])
@restricted
def start_ollama(message: types.Message):
    if not os.environ.get("POLLING"):
        bot.reply_to(message, "Running as webhook, please start on VM bot.")
    OllamaRunner().start_ollama()
    bot.reply_to(message, "Ollama started")


@bot.message_handler(commands=["stop_ollama"])
@restricted
def stop_ollama(message: types.Message):
    OllamaRunner().stop_ollama()
    bot.reply_to(message, "Ollama stopped")


@bot.message_handler(commands=["get_models"])
@restricted
def get_models(message: types.Message):
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
@restricted
def chat(message: types.Message):
    runner = OllamaRunner()
    if runner.process is None:
        bot.reply_to(message, "Ollama is not running. Start it with /start_ollama")
        return

    agent_prompt = runner.agent_choice(message.text)
    response = runner.chat(agent_prompt + message.text)
    bot.reply_to(message, response)

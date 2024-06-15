import os

import telebot
from google.cloud.run_v2.services.services.client import ServicesClient

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def _get_public_url():
    project_id = os.environ["PROJECT_ID"]
    region = os.environ["REGION"]
    service = os.environ["SERVICE_NAME"]
    full_service_name = f"projects/{project_id}/locations/{region}/services/{service}"

    client = ServicesClient()
    resp = client.get_service(name=full_service_name)
    return resp.uri


def set_webook(webhook_path):
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()
    webhook_url = _get_public_url() + webhook_path
    bot.set_webhook(url=webhook_url)

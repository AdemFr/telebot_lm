import logging
import os
from contextlib import asynccontextmanager

import telebot
from fastapi import FastAPI

from telebot_lm import webhook
from telebot_lm.bot import bot
from telebot_lm.ollama_runner import OllamaRunner

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook.attach()
    yield
    webhook.detach()


app = FastAPI(docs=None, redoc_url=None, lifespan=lifespan)


@app.get("/")
async def root():
    return ""


@app.post(webhook.WEBHOOK_PATH)
def process_webhook(update: dict):
    """Processes webhook calls and passes them to message handlers."""
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


if __name__ == "__main__":
    if os.environ.get("POLLING"):
        try:
            bot.remove_webhook()  # Otherwise polling breaks when one still exists
            logger.info("Starting polling bot...")
            bot.infinity_polling()
        finally:
            OllamaRunner().stop_ollama()

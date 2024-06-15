import telebot
from fastapi import FastAPI

from telebot_lm.bot import bot, set_webook

app = FastAPI(docs=None, redoc_url=None)
WEBHOOK_PATH = "/webhook"
set_webook(WEBHOOK_PATH)


@app.get("/")
async def root():
    return ""


@app.post(WEBHOOK_PATH)
def process_webhook(update: dict):
    """Processes webhook calls and passes them to message handlers."""
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


if __name__ == "__main__":
    bot.infinity_polling()

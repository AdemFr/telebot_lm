import logging
import os

from google.cloud.run_v2.services.services.client import ServicesClient

from telebot_lm.bot import bot

logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/webhook"


def _get_public_url():
    if os.environ.get("POLLING"):
        return ""
    logger.info("Getting public URL...")
    project_id = os.environ["PROJECT_ID"]
    region = os.environ["REGION"]
    service = os.environ["SERVICE_NAME"]
    full_service_name = f"projects/{project_id}/locations/{region}/services/{service}"

    client = ServicesClient()
    resp = client.get_service(name=full_service_name)
    logger.info(f"{resp=}")
    logger.info(f"{dir(resp)=}")
    logger.info(f"Public URL: {resp.uri}")
    return resp.uri


def attach():
    """NOTE When deploying for the first time, this will fail, because there is no public URL yet."""
    if os.environ.get("POLLING"):
        return
    logger.info("Setting webhook...")
    webhook_url = _get_public_url() + WEBHOOK_PATH
    bot.set_webhook(url=webhook_url)
    logger.info("Setting webhook...OK")


def detach():
    if os.environ.get("POLLING"):
        return
    logger.info("Removing webhook...")
    bot.remove_webhook()

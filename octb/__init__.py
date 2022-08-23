import logging
import sys
from decouple import config
from telegram.ext import ApplicationBuilder

STORAGE=config('STORAGE')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f"{STORAGE}/logs.log",
    filemode='a',
)
LOGGER = logging.getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    LOGGER.error("You MUST have a python version of at least 3.8! Multiple features depend on this. Bot quitting.")
    quit(1)

LOGS_CHANNEL_ID=config('LOGS_CHANNEL_ID')
async def LOGGER_CHAT(text: str, lvl="INFO"):
    if lvl=="INFO":
        LOGGER.info(f"TELEGRAM - {text}")
    await application.bot.send_message(chat_id=LOGS_CHANNEL_ID, text=text)

# env
from decouple import config

TOKEN=config('TOKEN')

# main
application = ApplicationBuilder().token(TOKEN).build()
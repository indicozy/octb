import logging
import sys
from telegram.ext import ApplicationBuilder

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 10:
    LOGGER.error("You MUST have a python version of at least 3.10! Multiple features depend on this. Bot quitting.")
    quit(1)


# env
from decouple import config

TOKEN=config('TOKEN')

# main
application = ApplicationBuilder().token(TOKEN).build()
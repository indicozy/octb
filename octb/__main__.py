# environment
from decouple import config

# telegram bot
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

from octb import application
from octb.modules import ALL_MODULES

from octb.modules.sql import generator

import importlib

IMPORTED = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("octb.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

def main():
    application.run_polling()

if __name__ == '__main__':
    generator.generate_categories()
    main()

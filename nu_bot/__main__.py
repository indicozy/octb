# environment
from decouple import config

# telegram bot
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

from nu_bot.modules.sql.base import Session, engine
import nu_bot.modules.sql.base as db
from nu_bot.modules import private, products

def add_all_handlers(application):
    # handlers
    private_handlers = [
            private.startHandler,
            products.add_product,
            products.edit_handler,
        ]

    all_handlers = [
           private_handlers 
        ]

    for handler_group in all_handlers:
        for handler in handler_group:
            application.add_handler(handler)
    application.add_handler(private.handler_private_default)

def main():
    application.run_polling()
    add_all_handlers(application)

if __name__ == '__main__':
    db.create_tables()
    main()

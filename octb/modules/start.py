from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

from octb.modules.buttons import base as buttons
import octb.modules.sql.user as sql

from octb import application

__mod_name__ = "start"

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    sql.update_user(user.id, user.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=buttons.BASE_BUTTONS)

async def default_reply(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Повторите ваш запрос.", reply_markup=buttons.BASE_BUTTONS)

# handlers
startHandler = CommandHandler('start', start)
private_default = MessageHandler(filters.ALL & filters.ChatType.PRIVATE, default_reply)

application.add_handlers([startHandler, private_default])
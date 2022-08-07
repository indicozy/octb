from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

from nu_bot.modules.buttons import base as buttons
from nu_bot.modules.sql import base as db

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.create_user(user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=buttons.BASE_BUTTONS)

async def default_reply(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Повторите ваш запрос.")

# handlers
startHandler = CommandHandler('start', start)
handler_private_default = MessageHandler(filters.ALL & filters.ChatType.PRIVATE, default_reply)
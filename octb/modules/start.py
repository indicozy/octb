from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

import octb.modules.sql.user as sql

from octb import application, LOGGER_CHAT

__mod_name__ = "start"

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    sql.update_user(user.id, user.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Со мной вы можете купить еду, заказать донер, арендовать велосипед и многое другое! Нажмите на кнопку 'Магазин' чтобы посмотреть ассортимент.\n\nМой функционал будет расти в будущем, ждите обнов!",
                                   reply_markup=ReplyKeyboardRemove())

async def show_id(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(user.id))

async def show_id_chat(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update.effective_chat.id))

async def default_reply(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Повторите ваш запрос.",
                                   reply_markup=ReplyKeyboardRemove())

# handlers
startHandler = CommandHandler('start', start, filters=filters.ChatType.PRIVATE)
show_id_handler = CommandHandler('id', show_id_chat, filters=filters.ChatType.CHANNEL | filters.ChatType.GROUP)
show_id_chat_handler = CommandHandler('id', show_id, filters=filters.ChatType.PRIVATE)
private_default = MessageHandler(filters.ALL & filters.ChatType.PRIVATE, default_reply)

application.add_handlers([startHandler,show_id_handler, show_id_chat_handler, private_default])
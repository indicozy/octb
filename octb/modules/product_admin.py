__mod_name__ = "product_admin"

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb import application

from decouple import config
SUPERADMIN_ID=int(config('SUPERADMIN_ID'))


async def add_seller(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    print(user.id,SUPERADMIN_ID)
    print(user.id != SUPERADMIN_ID)
    if user.id != SUPERADMIN_ID:
        await update.message.reply_text("У вас нет прав")
        return
    if len(text.split(" ")) != 2 or not text.split(" ")[1].isdigit():
        await update.message.reply_text("Please send user id")
        return
    
    seller_id = int(text.split(" ")[1]) 
    sql.add_seller(seller_id)

    message_sent = False
    try:
        await context.bot.send_message(chat_id=seller_id, text="Вы добавлены в продавцы!")
        message_sent = True
    except Exception as e:
        LOGGER.warning(str(e))

    if message_sent:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавлено, сообщение отправлено")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Добавлено, сообщение НЕ отправлено")

async def remove_seller(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if user.id != SUPERADMIN_ID:
        await update.message.reply_text("У вас нет прав")
        return

    if len(text.split(" ")) != 2 or not text.split(" ")[1].isdigit():
        await update.message.reply_text("Please send user id")
        return
        
    seller_id = int(text.split(" ")[1]) 
    success = sql.remove_seller(seller_id)

    message_sent = False
    try:
        if success:
            await context.bot.send_message(chat_id=seller_id, text="Вы удалены из продавцов.")
            message_sent = True
    except Exception as e:
        LOGGER.warning(str(e))

    response = "Удалено"

    if success:
        if message_sent:
            response += ", сообщение отправлено"
        else:
            response += ", сообщение НЕ отправлено"
    else:
        response += ", продавца не найдено"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

add_seller_handler = CommandHandler('add_seller', add_seller, filters=filters.ChatType.PRIVATE)
remove_seller_handler = CommandHandler('remove_seller', remove_seller, filters=filters.ChatType.PRIVATE)

application.add_handlers([add_seller_handler, remove_seller_handler])

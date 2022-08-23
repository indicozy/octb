from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

import octb.modules.sql.user as sql_user
import octb.modules.sql.product as sql_product
import asyncio

from octb import application

__mod_name__ = "admin"

from decouple import config
SUPERADMIN_ID=int(config('SUPERADMIN_ID'))

async def stats(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text

    if user.id != SUPERADMIN_ID:
        await update.message.reply_text("У вас нет прав")
        return
    
    users_count = sql_user.count_users()
    products_count = sql_product.count_products()
    bought_items_count = sql_product.count_product_buyers()

    users = sql_user.get_users_all()

    await update.message.reply_text(text=f"Users: {users_count}\nProduct: {products_count}\nBought_items: {bought_items_count}")

async def sendall(update: Update, context:ContextTypes.DEFAULT_TYPE):
    async def send_message(user_id, text):
        try: 
            await context.bot.send_message(chat_id=user_id, text=text)
            return True
        except:
            return False

    user = update.message.from_user
    user_text = update.message.text

    if user.id != SUPERADMIN_ID:
        await update.message.reply_text("У вас нет прав")
        return

    command = user_text.split("\n")[0].split(" ")
    if "-y" not in command:
        await update.message.reply_text("Вы не подтвердили отправку с помощью -y")
        return
        
    text = "\n".join(user_text.split("\n")[1:])
    if text == "":
        await update.message.reply_text("Нет текста.")
        return

    users = sql_user.get_users_all()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Отправляем сообщение:\n\n{text}\n\n{len(users)} пользователям...")

    is_sent_list = await asyncio.gather(*[send_message(user.user_id, text) for user in users]) # TODO check if it won't break up

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сообщение отправлено:\n\n{text}\n\n{sum(is_sent_list)} пользователей получили, {len(is_sent_list) - sum(is_sent_list)} пользователей  НЕ получили сообщения")

# handlers
sendall_handler = CommandHandler('sendall', sendall, filters=filters.ChatType.PRIVATE)
stats_handler = CommandHandler('stats', stats, filters=filters.ChatType.PRIVATE)

application.add_handlers([sendall_handler, stats_handler])
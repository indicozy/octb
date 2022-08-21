from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler

from octb.modules.buttons import base as buttons
import octb.modules.sql.user as sql
import asyncio

from octb import application

__mod_name__ = "admin"

from decouple import config
SUPERADMIN_ID=int(config('SUPERADMIN_ID'))

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

    users = sql.get_users_all()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Отправляем сообщение:\n\n{text}\n\n{len(users)} пользователям...", reply_markup=buttons.BASE_BUTTONS)

    is_sent_list = await asyncio.gather(*[send_message(user.user_id, text) for user in users]) # TODO check if it won't break up

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сообщение отправлено:\n\n{text}\n\n{sum(is_sent_list)} пользователей получили, {len(is_sent_list) - sum(is_sent_list)} пользователей  НЕ получили сообщения", reply_markup=buttons.BASE_BUTTONS)

# handlers
sendall_handler = CommandHandler('sendall', sendall, filters=filters.ChatType.PRIVATE)

application.add_handlers([sendall_handler])
__mod_name__ = "product_admin"

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb import application

from decouple import config
SUPERADMIN_ID=int(config('SUPERADMIN_ID'))


async def add_seller(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
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

async def edit_seller_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    await query.answer()
    await context.bot.send_message( chat_id=user.id,
            text="Напишите название магазина, для отмены пишите 'Отмена'")
    return EDIT_NAME

async def edit_seller_name_text(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if text.lower() != 'отмена':
        sql.update_seller_name(user.id, text)
    await edit_seller(update, context)
    return ConversationHandler.END

async def edit_seller_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    await query.answer()
    await context.bot.send_message( chat_id=user.id,
            text="Имеете ли вы доставку? Да/Нет/Отмена")
    return EDIT_DELIVERY

async def edit_seller_delivery_text(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if text.lower() != 'отмена':
        if text.lower() == 'да':
            sql.update_seller_delivery(user.id, True)
        elif text.lower() == 'нет':
            sql.update_seller_delivery(user.id, False)
        else:
            await update.message.reply_text("Да/Нет/Отмена?")
            return EDIT_DELIVERY
            
    await edit_seller(update, context)
    return ConversationHandler.END

async def edit_seller_working_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    await query.answer()
    await context.bot.send_message( chat_id=user.id,
            text="Напишите время работы магазина, для отмены пишите 'Отмена'")
    return EDIT_WORKING_TIME

async def edit_seller_working_time_text(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if text.lower() != 'отмена':
        sql.update_seller_working_time(user.id, text)
    await edit_seller(update, context)
    return ConversationHandler.END

async def edit_seller_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    await query.answer()
    await context.bot.send_message( chat_id=user.id,
            text="Напишите номер телефона (каспи) магазина, для отмены пишите 'Отмена'")
    return EDIT_PHONE_NUMBER

async def edit_seller_phone_number_text(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if text.lower() != 'отмена':
        sql.update_seller_phone_number(user.id, text)
    await edit_seller(update, context)
    return ConversationHandler.END

async def edit_seller_instant_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    await query.answer()
    await context.bot.send_message( chat_id=user.id,
            text="Напишите мгновенное сообщение магазина, для отмены пишите 'Отмена'")
    return EDIT_PHONE_NUMBER

async def edit_seller_instant_message_text(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    if text.lower() != 'отмена':
        sql.update_seller_instant_message(user.id, text)
    await edit_seller(update, context)
    return ConversationHandler.END

async def edit_seller(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    seller = sql.get_seller_by_user_id(user.id)
    
    if not seller:
        await update.message.reply_text("Вы не являетесь продавцом")
        return

    menu = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Название", callback_data="SELLER_NAME"),
            InlineKeyboardButton("Доставка", callback_data="SELLER_DELIVERY")
         ],
        [
            InlineKeyboardButton("Время Работы", callback_data="SELLER_TIME"),
            InlineKeyboardButton("Номер Телефона", callback_data="SELLER_NUMBER")
            ],
        [
            InlineKeyboardButton("Мгновенное сообщение", callback_data="SELLER_MESSAGE"),
            ],
        ]) 
    
    await update.message.reply_text(text=f"Название: {seller.name}\nДоставка:{'есть' if seller.has_delivery else 'нету'}\n"
                                        f"Время Работы: {seller.working_time}\nТелефон(Kaspi): {seller.phone_number}"
                                    , reply_markup=menu)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    LOGGER.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


add_seller_handler = CommandHandler('add_seller', add_seller, filters=filters.ChatType.PRIVATE)
remove_seller_handler = CommandHandler('remove_seller', remove_seller, filters=filters.ChatType.PRIVATE)

EDIT_NAME,EDIT_DELIVERY, EDIT_WORKING_TIME, EDIT_PHONE_NUMBER = range(4)

edit_seller_handler = CommandHandler('edit_seller', edit_seller, filters=filters.ChatType.PRIVATE)
edit_seller_name_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(edit_seller_name, pattern="^" + "SELLER_NAME" + "$")
        ],
    states={
        EDIT_NAME: [
            MessageHandler(~filters.COMMAND & filters.TEXT, edit_seller_name_text),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

edit_seller_delivery_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(edit_seller_delivery, pattern="^" + "SELLER_DELIVERY" + "$")
        ],
    states={
        EDIT_DELIVERY: [
            MessageHandler(~filters.COMMAND & filters.TEXT, edit_seller_delivery_text),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

edit_seller_working_time_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(edit_seller_working_time, pattern="^" + "SELLER_TIME" + "$")
        ],
    states={
        EDIT_WORKING_TIME: [
            MessageHandler(~filters.COMMAND & filters.TEXT, edit_seller_working_time_text),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

edit_seller_phone_number_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(edit_seller_phone_number, pattern="^" + "SELLER_NUMBER" + "$")
        ],
    states={
        EDIT_PHONE_NUMBER: [
            MessageHandler(~filters.COMMAND & filters.TEXT, edit_seller_phone_number_text),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

edit_seller_instant_message_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(edit_seller_instant_message, pattern="^" + "SELLER_MESSAGE" + "$")
        ],
    states={
        EDIT_PHONE_NUMBER: [
            MessageHandler(~filters.COMMAND & filters.TEXT, edit_seller_instant_message_text),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

edit_seller_handlers = [
    edit_seller_handler,
    edit_seller_name_handler,
    edit_seller_delivery_handler,
    edit_seller_working_time_handler,
    edit_seller_phone_number_handler,
    edit_seller_instant_message_handler,
]

application.add_handlers([add_seller_handler, remove_seller_handler] + edit_seller_handlers)

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb.modules.helpers.product import generate_post_product
from octb.modules.helpers.base import generate_post
from octb.modules.helpers.review import star_generate

from octb import application

review_preps = {}

async def review_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("REVIEW_", "")
    LOGGER.info("callback of %s: %s", user.id, text)

    item = sql.get_product_by_id_no_verify(product_id) # TODO add verification of callback
    seller = sql.get_seller_by_product_id(product_id)

    review_preps[user.id] = {}
    review_preps[user.id]["product"] = item

    await query.answer()

    await context.bot.send_message( #TODO add edit context for photos
        chat_id=user.id,
        text=f"Вы оставляете оценку:\n{item.name}\nПродавец:\n{seller.name}. Поставьте оценку от 1-5 ниже, для отмены напишите /cancel:"
        )
    return REVIEW_POINTS

async def review_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("callback of %s: %s", user.id, user_text)

    if not user_text.isdigit() or (int(user_text) < 1 or int(user_text) > 5):
        await update.message.reply_text("Напишите от 1 до 5:")
        return REVIEW_POINTS

    review_preps[user.id]["points"] = int(user_text)

    await update.message.reply_text( #TODO add edit context for photos
        text=f"Опишите что вам понравилось или ваши предложения, чтобы оставить текст пустым, напишите Пропустить, для отмены напишите /cancel:"
        )
    return REVIEW_DESCRIPTION

async def review_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("callback of %s: %s", user.id, user_text)

    review_preps[user.id]["description"] = user_text
    if user_text.lower() == 'пропустить':
        review_preps[user.id]["description"] = ""

    sql.add_review(review_preps[user.id]["product"].id, user.id,
                   points=review_preps[user.id]["points"], description=review_preps[user.id]["description"])

    message_seller = await context.bot.send_message(chat_id=review_preps[user.id]["product"].seller_id,
                                                    text=f"У вас новая рецензия!\n\n{star_generate(review_preps[user.id]['points'])}\n"
                                                    f"{review_preps[user.id]['description']}"
                                                    )

    await update.message.reply_text( #TODO add edit context for photos
        text=f"Спасибо за ответ!"
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    LOGGER.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

REVIEW_POINTS, REVIEW_DESCRIPTION = range(2)

review_product_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(review_product, pattern="^REVIEW_")
        ],
    states={
        REVIEW_POINTS: [
            MessageHandler(~filters.COMMAND & filters.TEXT, review_points),
            ],
        REVIEW_DESCRIPTION: [
            MessageHandler(~filters.COMMAND & filters.TEXT, review_description),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handlers([review_product_handler])
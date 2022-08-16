from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb.modules.helpers.product import generate_post_product
from octb.modules.helpers.base import generate_post
from octb.modules.helpers.review import star_generate

from octb import application

# TODO add redis
buyer_preps = {}
bought_preps = {}

__mod_name__ = "marketplace"

from decouple import config
STORAGE=config('STORAGE')

async def marketplace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    buyer_preps[user.id] = {}

    categories = sql.get_all_categories()
    buyer_preps[user.id]['categories'] = categories
    text = "\n".join([f"{index + 1}. {category.name}" for category, index in zip(categories, range(len(categories)))])

    await update.message.reply_text(
        text
    )

    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    user_text = update.message.text

    if not user_text.isdigit():
        await update.message.reply_text("выберите число")
        return CATEGORY

    buyer_preps[user.id]['category'] =  buyer_preps[user.id]['categories'][int(user_text) - 1]

    subcategories = sql.get_subcategories_by_category_id(int(user_text))
    buyer_preps[user.id]['subcategories'] = subcategories

    text = "\n".join([f"{index + 1}. {subcategory.name}" for subcategory, index in zip(subcategories, range(len(subcategories)))])

    await update.message.reply_text(
        text
    )

    return SUBCATEGORY

async def subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    user_text = update.message.text

    if not user_text.isdigit():
        await update.message.reply_text("выберите число")
        return SUBCATEGORY

    buyer_preps[user.id]['subcategory'] =  buyer_preps[user.id]['subcategories'][int(user_text) - 1]

    products = sql.get_product_sellers_by_subcategory(buyer_preps[user.id]['subcategory'].id)
    buyer_preps[user.id]['products'] = products

    text = ""
    for product, index in zip(products, range(len(products))):
        reviews_sum, reviews_amount = sql.get_reviews_by_product_id(product.id)
        bought_amount = sql.get_buyer_count_by_product_id(product.id)
        text += f"{index + 1}. {star_generate(reviews_sum)} ({reviews_amount}) {product.name} ({bought_amount})" 

    await update.message.reply_text(
        text
    )

    return PRODUCT

async def product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    user_text = update.message.text

    if not user_text.isdigit():
        await update.message.reply_text("выберите число")
        return PRODUCT

    buyer_preps[user.id]['product'] =  buyer_preps[user.id]['products'][int(user_text) - 1]

    product = sql.get_product_by_id_no_verify(buyer_preps[user.id]['product'].id)

    buyer_preps.pop(user.id) # TODO try except

    menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить", callback_data="BUY_SELLER_" + str(product.id))],
        ]) 

    if product.has_image:
        storage_folder = f'{STORAGE}/photos/product/'
        await update.message.reply_photo(
            photo=open(f"{storage_folder}{product.id}.jpg", 'rb'),
            caption=generate_post_product(product),
            reply_markup=menu
        )
    else:
        await update.message.reply_text(
            generate_post_product(product),
            reply_markup=menu
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

async def buy_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("BUY_SELLER_", "")
    LOGGER.info("callback of %s: %s", user.id, text)

    item = sql.get_product_by_id_no_verify(product_id) # TODO add verification of callback
    seller = sql.get_seller_by_product_id(product_id)

    seller_menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Контакты", url=f"tg://user?id={user.id}"),
            ],
        ]
    ) 

    if item.has_image:
        storage_folder = f'{STORAGE}/photos/product/'
        message_seller = await context.bot.send_photo(
            photo=open(f"{storage_folder}{item.id}.jpg", 'rb'),
            chat_id=seller.user_id, caption=f"У вас есть покупатель!\n\n{item.name}\n\nАдрес: неизвестно", reply_markup=seller_menu)
    else:
        message_seller = await context.bot.send_message(chat_id=seller.user_id, text=f"У вас есть покупатель!\n\n{item.name}\n\nАдрес: неизвестно", reply_markup=seller_menu)

    sql.add_buyer(product_id, user.id, message_id=message_seller.id)
    bought_preps[user.id] = {}
    bought_preps[user.id]["seller_id"] = seller.user_id
    bought_preps[user.id]["message_id"] = message_seller.id
    bought_preps[user.id]["product"] = item

    menu = ReplyKeyboardMarkup([
        [
            'Нет адреса',
        ]
    ], one_time_keyboard=True)

    await query.answer()

    instant_message = f'Сообщение от продавца:\n{seller.instant_message}\n\n' if seller.instant_message else ''

    await context.bot.send_message( #TODO add edit context for photos
        chat_id=user.id,
        text=f"Вы покупаете:\n{item.name}\nЦена: {item.price}\n\nПродавец: {seller.name}\nВремя работы: {seller.working_time}\nДоставка: {'есть' if seller.has_delivery else 'нету'}\nТелефон: {seller.phone_number}\nСсылка на паблик: {seller.link}\n\n"
        f"{instant_message}"
        f"Напишите свой адрес или напишите 'Нет адреса' для доставки.",
        reply_markup=menu)
    return SEND_ADDRESS

async def send_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text

    LOGGER.info("callback of %s: %s", user.id, user_text)

    seller_id = bought_preps[user.id]["seller_id"]
    message_id = bought_preps[user.id]["message_id"]
    product = bought_preps[user.id]["product"]

    seller_menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Контакты", url=f"tg://user?id={user.id}"),
            ],
            [
                InlineKeyboardButton("Закрыть Объявление", callback_data=f"SOLD_{product.id}"),
            ]
        ]
    ) 

    buyer_menu = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Оставить Оценку", callback_data="REVIEW_" + str(product.id))],
            # [InlineKeyboardButton("Отменить Покупку", callback_data="REVIEW_" + str(product.id))],
        ]
    ) 

    if product.has_image:
        await context.bot.edit_message_caption(
            chat_id=seller_id, message_id=message_id,
            caption=f"У вас есть покупатель!\n\n{product.name}\n\nАдрес: {user_text}", reply_markup=seller_menu)
    else:
        await context.bot.edit_message_text(chat_id=seller_id, message_id=message_id, text=f"У вас есть покупатель!\n\n{product.name}\n\nАдрес: {user_text}", reply_markup=seller_menu)


    await context.bot.send_message( #TODO add edit context for photos
        chat_id=user.id,
    text="Адрес принят. Ожидайте заказа!", reply_markup=buyer_menu)
    return ConversationHandler.END

CATEGORY, SUBCATEGORY, PRODUCT = range(3)

# main
marketplace = ConversationHandler(
    entry_points=[
            # CallbackQueryHandler(new_product, pattern="^" + "PRODUCT_NEW" + "$"),
            MessageHandler(filters.TEXT & filters.Regex('^Магазин$') & filters.ChatType.PRIVATE, marketplace),
            CommandHandler("marketplace", marketplace, filters=filters.ChatType.PRIVATE),
        ],
    states={
        CATEGORY: [
            MessageHandler(~filters.COMMAND & filters.TEXT, category)],
        SUBCATEGORY: [
            MessageHandler(~filters.COMMAND & filters.TEXT, subcategory)],
        PRODUCT: [
            MessageHandler(~filters.COMMAND & filters.TEXT, product),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
SEND_ADDRESS, = range(1)

buy_seller_handler = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(buy_seller_callback, pattern="^BUY_SELLER_")
        ],
    states={
        SEND_ADDRESS: [
            MessageHandler(~filters.COMMAND & filters.TEXT, send_address),
            ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handlers([marketplace, buy_seller_handler])
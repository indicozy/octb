from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb.modules.helpers.product import generate_post_product
from octb.modules.helpers.review import star_generate
from octb.modules.helpers.base import generate_post, generate_menu

from octb import application

# TODO add redis
bought_preps = {}

__mod_name__ = "marketplace"

from decouple import config
STORAGE=config('STORAGE')

def TEXT_GOT_SELLER(product, info):
    return f"У вас есть покупатель!\n\n{product.name}\n\nАдрес: {info}"

async def marketplace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user

    categories = sql.get_all_categories()
    # text = "\n".join([f"{index + 1}. {category.name}" for category, index in zip(categories, range(len(categories)))])
    text = "Выберите категорию:"

    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(f"{category.name}",
                                    callback_data="MARKETPLACE_CATEGORY_" + str(category.id)) for category, index in zip(categories, range(len(categories)))])
                                )

    await update.message.reply_text(
        text, reply_markup=menu
    )

async def marketplace_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    query = update.callback_query

    user = update.callback_query.from_user
    user_text = query.data

    categories = sql.get_all_categories()
    # text = "\n".join([f"{index + 1}. {category.name}" for category, index in zip(categories, range(len(categories)))])
    text = "Выберите категорию:"

    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(f"{category.name}",
                                    callback_data="MARKETPLACE_CATEGORY_" + str(category.id)) for category, index in zip(categories, range(len(categories)))])
                                )

    await query.edit_message_text(
        text, reply_markup=menu
    )

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    query = update.callback_query

    user = update.callback_query.from_user
    user_text = query.data
    category_id = user_text.replace("MARKETPLACE_CATEGORY_", "")
    category = sql.get_category_by_id(category_id)

    subcategories = sql.get_subcategories_by_category_id(int(category_id))
    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(f"{subcategory.name}",
                                    callback_data="MARKETPLACE_SUBCATEGORY_" + str(subcategory.id)) for subcategory, index in zip(subcategories, range(len(subcategories)))])
                                    + [[InlineKeyboardButton(f"< Назад", callback_data="MARKETPLACE_START")]]
                                )

    # text = "\n".join([f"{index + 1}. {subcategory.name}" for subcategory, index in zip(subcategories, range(len(subcategories)))])
    text = f"Категория: {category.name}\n\nВыберите подкатегорию:"

    await query.edit_message_text(
        text=text,
        reply_markup=menu
    )

async def subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    query = update.callback_query

    user = update.callback_query.from_user
    user_text = query.data
    subcategory_id = user_text.replace("MARKETPLACE_SUBCATEGORY_", "")

    subcategory = sql.get_subcategory_by_id(subcategory_id)
    products = sql.get_product_sellers_by_subcategory(int(subcategory_id))
    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(f"{index + 1}",
                                    callback_data="MARKETPLACE_PRODUCT_" + str(product.id)) for product, index in zip(products, range(len(products)))])
                                    + [[InlineKeyboardButton(f"< Назад", callback_data="MARKETPLACE_CATEGORY_" + str(subcategory.category_id))]]
                                )

    text = f"Подкатегория: {subcategory.name}\n\nВыберите товар:\n"
    for product, index in zip(products, range(len(products))):
        reviews_sum, reviews_amount = sql.get_reviews_by_product_id(product.id)
        bought_amount = sql.get_buyer_count_by_product_id(product.id)
        text += f"{index + 1}. {star_generate(reviews_sum)} ({reviews_amount}) {product.name} {product.price}₸" 

    await query.edit_message_text(
        text,
        reply_markup=menu
    )

async def product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    query = update.callback_query
    await query.delete_message()

    user = update.callback_query.from_user
    user_text = query.data
    product_id = user_text.replace("MARKETPLACE_PRODUCT_", "")

    product = sql.get_product_by_id_no_verify(int(product_id))

    menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить", callback_data="BUY_SELLER_" + str(product.id))],
        [InlineKeyboardButton(f"< Назад", callback_data="MARKETPLACE_SUBCATEGORY_" + str(product.subcategory_id))],
        ]) 

    if product.has_image:
        storage_folder = f'{STORAGE}/photos/product/'
        await context.bot.send_message(
            chat_id=user.id,
            photo=open(f"{storage_folder}{product.id}.jpg", 'rb'),
            caption=generate_post_product(product),
            reply_markup=menu
        )
    else:
        await context.bot.send_message(
            chat_id=user.id,
            text=generate_post_product(product),
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
            chat_id=seller.user_id, caption=TEXT_GOT_SELLER(item, 'неизвестно'), reply_markup=seller_menu)
    else:
        message_seller = await context.bot.send_message(chat_id=seller.user_id, text=TEXT_GOT_SELLER(item, 'неизвестно'), reply_markup=seller_menu)

    sql.add_buyer(product_id, user.id, message_id=message_seller.id)
    bought_preps[user.id] = {}
    bought_preps[user.id]["seller_id"] = seller.user_id
    bought_preps[user.id]["message_id"] = message_seller.id
    bought_preps[user.id]["product"] = item

    menu = ReplyKeyboardMarkup([
        [
            'Нет данных',
        ]
    ], one_time_keyboard=True)

    await query.answer()

    instant_message = f'Сообщение от продавца:\n{seller.instant_message}\n\n' if seller.instant_message else ''

    await context.bot.send_message( #TODO add edit context for photos
        chat_id=user.id,
        text=f"Вы покупаете:\n{item.name}\nЦена: {item.price}\n\nПродавец: {seller.name}\nВремя работы: {seller.working_time}\nДоставка: {'есть' if seller.has_delivery else 'нету'}\nТелефон: {seller.phone_number}\nСсылка на паблик: {seller.link}\n\n"
        f"{instant_message}"
        f"Напишите информацию о себе (Адрес, имя, кол-во продуктов) или напишите 'Нет данных' для доставки.",
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
            caption=TEXT_GOT_SELLER(product, user_text), reply_markup=seller_menu)
    else:
        await context.bot.edit_message_text(chat_id=seller_id, message_id=message_id, text=TEXT_GOT_SELLER(product, user_text), reply_markup=seller_menu)


    await context.bot.send_message( #TODO add edit context for photos
        chat_id=user.id,
    text="Данные приняты. Ожидайте заказа!", reply_markup=buyer_menu)
    return ConversationHandler.END

# main
marketplace_start_1 = MessageHandler(filters.TEXT & filters.Regex('^Магазин$') & filters.ChatType.PRIVATE, marketplace)
marketplace_start_2 = CommandHandler("marketplace", marketplace, filters=filters.ChatType.PRIVATE)
marketplace_start_3 = CallbackQueryHandler(marketplace_callback, pattern="^" + "MARKETPLACE_START")
marketplace_category = CallbackQueryHandler(category, pattern="^" + "MARKETPLACE_CATEGORY_")
marketplace_subcategory = CallbackQueryHandler(subcategory, pattern="^" + "MARKETPLACE_SUBCATEGORY_")
marketplace_product = CallbackQueryHandler(product, pattern="^" + "MARKETPLACE_PRODUCT_")
marketplace_handlers = [
    marketplace_start_1,
    marketplace_start_2,
    marketplace_start_3,
    marketplace_category,
    marketplace_subcategory,
    marketplace_product,
]

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

application.add_handlers([buy_seller_handler] + marketplace_handlers)
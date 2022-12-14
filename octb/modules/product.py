from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as sql
from octb import LOGGER
from octb.modules.helpers.product import generate_post_product
from octb.modules.helpers.base import generate_post, generate_menu

from octb import application

# storage
import os

# TODO add redis
product_preps = {}

__mod_name__ = "product"

# env
from decouple import config
STORAGE=config('STORAGE')
MARKETPLACE_CHAT_ID=config('MARKETPLACE_CHAT_ID')
MARKETPLACE_CHAT_ACCOUNT=config('MARKETPLACE_CHAT_ACCOUNT')

buy_sell_button = ReplyKeyboardMarkup([
    [
        'Куплю',
        'Продаю',
    ],
    [
        'Сдаю',
        'Одолжу',
    ],
    [
        'Отдам',
    ]
], one_time_keyboard=True)

# conversation
async def new_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    product_preps[user.id] = {}

    await update.message.reply_text(
        "Выберите категорию", reply_markup=buy_sell_button
    )

    return PRODUCT_TYPE

async def new_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    query = update.callback_query
    await query.answer()

    user = update.callback_query.from_user
    text = query.data

    product_preps[user.id] = {}

    await context.bot.send_message( chat_id=user.id,
        text="Выберите категорию", reply_markup=buy_sell_button
    )

    return PRODUCT_TYPE

async def product_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    user_text = update.message.text.lower()

    if user_text in ['куплю', 'продаю', 'одолжу', 'сдаю',  'отдам']:
        product_preps[user.id]['product_type'] = sql.ProductTypeEnum(user_text.lower())
    else:
        await update.message.reply_text("Куплю/Продаю/Сдаю/Одолжу/Отдам?", reply_markup=buy_sell_button)
        return PRODUCT_TYPE
    
    await update.message.reply_text(
        "NAME"
        "Send /cancel to stop talking to me.\n\n"
    )

    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    product_preps[user.id]['name'] = update.message.text
    
    await update.message.reply_text(
        "Description"
        "Send /cancel to stop talking to me.\n\n"
    )

    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    product_preps[user.id]['description'] = update.message.text
    
    await update.message.reply_text(
        "price"
        "Send /cancel to stop talking to me.\n\n"
    )

    return PRICE

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send a description.", user.first_name)
    product_preps[user.id]['description'] = ""
    await update.message.reply_text(
        "I bet you look great! Now, send me your price please, or send /skip."
    )

    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    text = update.message.text
    LOGGER.info("price of %s: %s", user.first_name, update.message.text)
    if not text.isdigit():
        await update.message.reply_text("send price")
        return PRICE

    product_preps[user.id]['price'] = text
    
    await update.message.reply_text(
        "image"
        "Send /cancel to stop talking to me.\n\n"
    )

    return IMAGE

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user

    file_id = update.message.photo[-1].file_id
    newFile = await context.bot.getFile(file_id)

    storage_location = f'{STORAGE}/photos/temp/product/{user.id}.jpg'

    await newFile.download(storage_location)
    
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    product_preps[user.id]['photo_location'] = storage_location

    categories = sql.get_all_categories()
    product_preps[user.id]['categories'] = categories
    text = "\n".join([f"{index + 1}. {category.name}" for category, index in zip(categories, range(len(categories)))])

    await update.message.reply_text(text)

    return CATEGORY

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    product_preps[user.id]['photo_location'] = None

    categories = sql.get_all_categories()
    product_preps[user.id]['categories'] = categories
    text = "\n".join([f"{index + 1}. {category.name}" for category, index in zip(categories, range(len(categories)))])
    await update.message.reply_text(text)

    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("Choose a number")
        return CATEGORY
    product_preps[user.id]['category'] = product_preps[user.id]['categories'][int(update.message.text) - 1]

    subcategories = sql.get_subcategories_by_category_id(int(update.message.text))
    product_preps[user.id]['subcategories'] = subcategories

    text = "\n".join([f"{index + 1}. {subcategory.name}" for subcategory, index in zip(subcategories, range(len(subcategories)))])
    await update.message.reply_text(text)

    return SUBCATEGORY

async def subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("Choose a number")
        return SUBCATEGORY
    product_preps[user.id]['subcategory'] = product_preps[user.id]['subcategories'][int(update.message.text) - 1]

    await update.message.reply_text("y/n")

    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    def marketplace_text(name, description, product_type, category):
        return f"""#{product_type.value.lower()} #{category.lower()} \n{name}\n\n{description}\n\n @{MARKETPLACE_CHAT_ACCOUNT}"""

    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("text of %s: %s", user.first_name, update.message.text)

    message = None

    if user_text in ['N', 'n', "Нет", "нет"]:
        await update.message.reply_text(
            "Вы вернулись в главный экран"
        )
        return ConversationHandler.END

    elif user_text in ['y', 'Y', 'Да', 'да']:


        storage_folder = f'{STORAGE}/photos/product/'

        post_text = generate_post(product_preps[user.id]['name'], product_preps[user.id]['description'],
                                    [product_preps[user.id]['product_type'].value, product_preps[user.id]['category'].name,
                                        product_preps[user.id]['subcategory'].name
                                     ])

        if product_preps[user.id]['photo_location']:
            message = await context.bot.send_photo(chat_id=MARKETPLACE_CHAT_ID, photo=open(product_preps[user.id]['photo_location'], 'rb'),
                                                     caption=post_text)
        else: 
            message = await context.bot.send_message(chat_id=MARKETPLACE_CHAT_ID,
                                                     text=post_text)
        product_new = sql.add_product(message_id=message.message_id, product_type=product_preps[user.id]['product_type'], name=product_preps[user.id]['name'], description=product_preps[user.id]['description'],
                       price=product_preps[user.id]['price'], seller_id=user.id, subcategory=product_preps[user.id]['subcategory'].id, has_image= product_preps[user.id]['photo_location'] != None)
                       
        menu = InlineKeyboardMarkup([[InlineKeyboardButton("Купить", callback_data="BUY_PRODUCT_" + str(product_new.id))]]) 

        if product_preps[user.id]['photo_location']:
            message_edited = await context.bot.edit_message_caption(chat_id=MARKETPLACE_CHAT_ID, message_id = message.id,
                                                     caption=post_text,
                                                     reply_markup=menu)
        else:
            message_edited = await context.bot.edit_message_text(chat_id=MARKETPLACE_CHAT_ID, message_id = message.id,
                                                     text=post_text,
                                                     reply_markup=menu)

        await update.message.reply_text("Продукт добавлен!")

        if product_preps[user.id]['photo_location']:
            os.rename(product_preps[user.id]['photo_location'], f'{storage_folder}{product_new.id}.jpg')
            photo_location = storage_folder
        
        try:
            product_preps.pop(user.id) # TODO try except
        except:
            pass

        return ConversationHandler.END
    else:
        await update.message.reply_text( "Да/Нет?")

    return CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    LOGGER.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    try:
        product_preps.pop(user.id) # TODO try except
    except:
        pass

    return ConversationHandler.END


async def item_menu_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query

        user = update.callback_query.from_user
        text = query.data
    else:
        user = update.message.from_user
        text = update.message.text
        
    LOGGER.info("text of %s: %s", user.first_name, text)

    items = sql.get_active_products_from_tg_user(user.id)
    menu = InlineKeyboardMarkup([[InlineKeyboardButton("Создать Объявление", callback_data="PRODUCT_NEW")]] + generate_menu([InlineKeyboardButton(f"{'🔒' if item.is_sold else ''}{item.name[:20]}",
                                    callback_data="PRODUCT_MENU_" + str(item.id)) for item, index in zip(items, range(len(items)))]))


    if update.callback_query:
        await query.edit_message_text(
            "Ваши Объявления:", reply_markup=menu)
    else:
        await update.message.reply_text(
            "Ваши Объявления:", reply_markup=menu)

    return ITEM_MENU

async def item_menu_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("PRODUCT_MENU_", "")
    LOGGER.info("callback of %s: %s", user.id, text)

    item = sql.get_product_by_id(product_id, user.id) # TODO add verification of callback

    restore_or_sold = InlineKeyboardButton("Закрыть Объявление", callback_data=f"SELL_{product_id}")
    if item.is_sold:
        restore_or_sold = InlineKeyboardButton("Восстановить Объявление", callback_data=f"RESTORE_{product_id}") 

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Удалить Объявление", callback_data=f"ARCHIVE_{product_id}"),
            ],
            [
                restore_or_sold,
            ],
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    await query.edit_message_text(
        generate_post(headline=item.name, text=item.description, hashtags=[item.product_type.value, sql.get_category_by_subcategory_id(item.subcategory_id).name,  sql.get_subcategory_by_id(item.subcategory_id).name]), reply_markup=menu)
    return ConversationHandler.END

async def item_archive_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("ARCHIVE_", "")
    LOGGER.info("callback of %s: %s", user.id, text)

    item = sql.get_product_by_id(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Удалить", callback_data=f"ARCHIVE_CONFIRMED_{product_id}"),
            ],
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    await query.edit_message_text(
        generate_post_product(item) + \
            "ВЫ УВЕРЕНЫ ЧТО ХОТИТЕ УДАЛИТЬ? ПОСЛЕ УДАЛЕНИЯ ОБЪЯВЛЕНИЕ НЕЛЬЗЯ ВОССТАНОВИТЬ"
        , reply_markup=menu)
    return ConversationHandler.END

async def item_archive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("ARCHIVE_CONFIRMED_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_archived = sql.archive_product(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    post_deleted = False
    try:
        await context.bot.delete_message(chat_id=MARKETPLACE_CHAT_ID, # TODO add edit message first before deletion https://t.me/pythontelegrambotgroup/616535
                message_id=item_archived.message_id)
        post_deleted = True
    except:
        pass

    reply_text = "Не удалось удалить пост, но теперь никто не будет вам писать."
    if post_deleted:
        reply_text = "Пост удален."
    

    await query.edit_message_text(reply_text, reply_markup=menu)
    return ConversationHandler.END

async def inform_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data # TODO fix
    product_id = text.replace("BUY_PRODUCT_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item = sql.get_product_by_id_no_verify(product_id) # TODO add verification of callback

    if item.is_archived or item.is_sold:
        await query.answer(text='Продукт уже куплен или удален.', show_alert=True)
        return

    await query.answer(text='Мы написали продавцу, ожидайте от него/нее сообщения.', show_alert=True)

    item_bought = sql.add_buyer(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Контакты", url=f"tg://user?id={user.id}"),
            ],
            [
                InlineKeyboardButton("Закрыть Объявление", callback_data=f"SOLD_{product_id}"),
            ]
        ]
    ) 
    if item.has_image:
        storage_folder = f'{STORAGE}/photos/product/'
        await context.bot.send_photo(
            photo=open(f"{storage_folder}{item.id}.jpg", 'rb'),
            chat_id=item.seller_id, caption=f"Ваш продукт хотят купить!\n\n" + generate_post_product(item), reply_markup=menu)
    else:
        await context.bot.send_message(chat_id=item.seller_id, text=f"Ваш продукт хотят купить!\n\n" + generate_post_product(item), reply_markup=menu)


async def item_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("SELL_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_sold = sql.product_sold(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    reply_text = "Объявление закрыто. Вы больше не будете получать заявки."

    await query.edit_message_text(reply_text, reply_markup=menu)

async def item_sell_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query
    await query.answer()

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("SOLD_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_sold = sql.product_sold(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    reply_text = "Объявление закрыто. Вы больше не будете получать заявки."

    await context.bot.send_message(chat_id=user.id, text= reply_text, reply_markup=menu)

async def item_restore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("RESTORE_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_restored = sql.product_restore(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    reply_text = "Объявление восстановлено. Вы снова будете получать заявки."

    await query.edit_message_text(reply_text, reply_markup=menu)

PRODUCT_TYPE, NAME, DESCRIPTION, PRICE, IMAGE, CATEGORY, SUBCATEGORY, CONFIRMATION = range(8)

# main
add_product = ConversationHandler(
    entry_points=[
            CallbackQueryHandler(new_product_callback, pattern="^" + "PRODUCT_NEW" + "$"),
            # MessageHandler(filters.TEXT & filters.Regex('Купить/Продать') & filters.ChatType.PRIVATE, new_product),
            CommandHandler("new_item", new_product, filters=filters.ChatType.PRIVATE),
        ],
    states={
        PRODUCT_TYPE: [MessageHandler(~filters.COMMAND & filters.TEXT, product_type)],
        NAME: [MessageHandler(~filters.COMMAND & filters.TEXT, name)],
        DESCRIPTION: [
            MessageHandler(~filters.COMMAND & filters.TEXT, description),
            MessageHandler(filters.Regex('^Пропустить$'), skip_description),
            CommandHandler("skip", skip_description),
            ],
        PRICE: [
                MessageHandler(~filters.COMMAND & filters.TEXT, price),
            ],
        IMAGE: [
            MessageHandler(filters.PHOTO, image),

            MessageHandler(filters.Regex('^Пропустить$'), skip_image),
            CommandHandler("skip", skip_image),
        ],
        CATEGORY: [MessageHandler(~filters.COMMAND & filters.TEXT, category)],
        SUBCATEGORY: [MessageHandler(~filters.COMMAND & filters.TEXT, subcategory)],
        CONFIRMATION: [MessageHandler(~filters.COMMAND & filters.TEXT, confirmation)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

ITEM_MENU, ITEM_ARCHIVE, ITEM_MENU_ACTIONS, ITEM_BACK = range(4)

edit_start_1 = CommandHandler("my_items", item_menu_select)
edit_start_2 = MessageHandler(filters.Regex('^Мои Объявления$'), item_menu_select)
edit_start_3 = CallbackQueryHandler(item_menu_select, pattern="^" + "PRODUCT_START" + "$")
edit_item_menu = CallbackQueryHandler(item_menu_get_id, pattern="^" + "PRODUCT_MENU_")
edit_item_archive_confirm = CallbackQueryHandler(item_archive_confirmation, pattern="^" + "ARCHIVE_")
edit_item_has_sold  = CallbackQueryHandler(item_sell, pattern="^" + "SELL_")
edit_item_has_sold_reply  = CallbackQueryHandler(item_sell_reply, pattern="^" + "SOLD_")
edit_item_has_restored  = CallbackQueryHandler(item_restore, pattern="^" + "RESTORE_")

edit_item_has_archived = CallbackQueryHandler(item_archive, pattern="^" + "ARCHIVE_CONFIRMED_")
# edit_item_has_sold = CallbackQueryHandler(item_archive)

product_inform_seller = CallbackQueryHandler(inform_seller, pattern="^" + "BUY_PRODUCT_")

edit_handlers = [
    edit_start_1,
    edit_start_2,
    edit_start_3,
    edit_item_menu,
    edit_item_has_archived,
    edit_item_archive_confirm,
    edit_item_has_sold,
    edit_item_has_sold_reply,
    edit_item_has_restored,
]

application.add_handlers([add_product, product_inform_seller] + edit_handlers)
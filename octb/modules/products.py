from decouple import config
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.product as product_sql
import octb.modules.sql.category as category_sql
from octb import LOGGER
from octb.modules.helpers.base import generate_post, selling_map

from octb import application

# storage
import os

# TODO add redis
product_preps = {}

from decouple import config
MARKETPLACE_CHAT_ID=config('MARKETPLACE_CHAT_ID')

# env
STORAGE=config('STORAGE')
MARKETPLACE_CHAT_ID=config('MARKETPLACE_CHAT_ID')
MARKETPLACE_CHAT_ACCOUNT=config('MARKETPLACE_CHAT_ACCOUNT')

# conversation
async def new_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    product_preps[user.id] = {}

    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?"
    )

    return PRODUCT_TYPE

async def product_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    user_text = update.message.text

    if user_text in ['Купить', 'купить']:
        product_preps[user.id]['is_selling'] = False
    elif user_text in ['Продать', 'продать']:
        product_preps[user.id]['is_selling'] = True 
    else:
        await update.message.reply_text("Купить/Продать?")
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
        "image"
        "Send /cancel to stop talking to me.\n\n"
    )

    return IMAGE

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send a description.", user.first_name)
    product_preps[user.id]['description'] = ""
    await update.message.reply_text(
        "I bet you look great! Now, send me your image please, or send /skip."
    )

    return IMAGE

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user

    file_id = update.message.photo[-1].file_id
    newFile = await context.bot.getFile(file_id)

    storage_location = f'{STORAGE}/photos/temp/product/{user.id}.jpg'

    await newFile.download(storage_location)
    
    update.message.reply_text(text="download succesful")
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    product_preps[user.id]['photo_location'] = storage_location

    categories = category_sql.get_all_categories()
    text = "\n".join([f"{index + 1}. {category}" for category, index in zip(categories, range(len(categories)))])

    await update.message.reply_text(text)

    return CATEGORY

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    product_preps[user.id]['photo_location'] = None
    await update.message.reply_text(
        "I bet you look great! Now, send me your category please, or send /skip."
    )

    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    product_preps[user.id]['category'] = update.message.text

    await update.message.reply_text("y/n")

    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    def marketplace_text(name, description, is_selling, category):
        tag='куплю'
        if product_type:
            tag='продам'

        return f"""#{tag.lower()} #{category.lower()} \n{name}\n\n{description}\n\n @{MARKETPLACE_CHAT_ACCOUNT}"""

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

        if product_preps[user.id]['photo_location']:
            message = await context.bot.send_photo(chat_id=MARKETPLACE_CHAT_ID, photo=open(product_preps[user.id]['photo_location'], 'rb'),
                                                     caption=marketplace_text(product_preps[user.id]['name'], product_preps[user.id]['description'],
                                                                           product_preps[user.id]['is_selling'], product_preps[user.id]['category']))
        else: 
            message = await context.bot.send_message(chat_id=MARKETPLACE_CHAT_ID,
                                                     text=marketplace_text(product_preps[user.id]['name'], product_preps[user.id]['description'],
                                                                           product_preps[user.id]['is_selling'], product_preps[user.id]['category']))

        product_new = product_sql.add_product(message_id=message.id, is_selling=product_preps[user.id]['is_selling'], name=product_preps[user.id]['name'], description=product_preps[user.id]['description'],
                       seller_id=user.id, category_name=product_preps[user.id]['category'], has_image= product_preps[user.id]['photo_location'] != None)
                       
        menu = InlineKeyboardMarkup([[InlineKeyboardButton("Купить", callback_data="BUY_PRODUCT_" + str(product_new.id))]]) 

        message_edited = await context.bot.edit_message_text(chat_id=MARKETPLACE_CHAT_ID, message_id = message.id,
                                                     text=marketplace_text(product_preps[user.id]['name'], product_preps[user.id]['description'],
                                                                           product_preps[user.id]['is_selling'], product_preps[user.id]['category']),
                                                     reply_markup=menu)

        await update.message.reply_text("Продукт добавлен!")

        if product_preps[user.id]['photo_location']:
            os.rename(product_preps[user.id]['photo_location'], f'{storage_folder}{product_new.id}.jpg')
            photo_location = storage_folder

        product_preps.pop(user.id) # TODO try except
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

    return ConversationHandler.END


async def item_menu_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    def generate_menu(items):
        menu_new = [
            [],
        ]

        for i in items:
            if len(menu_new[-1]) >= 3:
                menu_new.append([i]) 
            else:
                menu_new[-1].append(i)
        return menu_new


    if update.callback_query:
        query = update.callback_query

        user = update.callback_query.from_user
        text = query.data
    else:
        user = update.message.from_user
        text = update.message.text
        
    LOGGER.info("text of %s: %s", user.first_name, text)

    items = product_sql.get_active_products_from_tg_user(user.id)
    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(item.name[:20], callback_data="PRODUCT_MENU_" + str(item.id)) for item, index in zip(items, range(len(items)))])) 


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

    item = product_sql.get_product_by_id(product_id, user.id) # TODO add verification of callback

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
        generate_post(headline=item.name, text=item.description, hashtags=[selling_map(item.is_selling), category_sql.get_category_by_id(item.category_id).name]), reply_markup=menu)
    return ConversationHandler.END

async def item_archive_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("ARCHIVE_", "")
    LOGGER.info("callback of %s: %s", user.id, text)

    item = product_sql.get_product_by_id(product_id, user.id) # TODO add verification of callback

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
        generate_post(headline=item.name, text=item.description, hashtags=[selling_map(item.is_selling), category_sql.get_category_by_id(item.category_id).name]) + \
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

    item_archived = product_sql.archive_product(product_id, user.id) # TODO add verification of callback

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

    item = product_sql.get_product_by_id_no_verify(product_id) # TODO add verification of callback
    print(item.is_archived, item.is_sold)
    print(item)

    if item.is_archived or item.is_sold:
        await query.answer(text='Продукт уже куплен или удален.', show_alert=True)
        return

    await query.answer(text='Мы написали продавцу, ожидайте от него/нее сообщения.', show_alert=True)

    item_bought = product_sql.set_buyer(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Контакты", url=f"tg://user?id={user.id}"),
            ]
        ]
    ) 

    await context.bot.send_message(chat_id=item_bought.seller_id, text=f"Ваш продукт хотят купить!\n\n" + generate_post(item_bought.name, item_bought.description, []), reply_markup=menu)

async def item_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("SELL_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_sold = product_sql.product_sold(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    reply_text = "Объявление закрыто. Вы больше не будете получать заявки."

    await query.edit_message_text(reply_text, reply_markup=menu)

async def item_restore(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query

    user = update.callback_query.from_user
    text = query.data
    product_id = text.replace("RESTORE_", "")
    LOGGER.info("callback of %s: %s", user.id, text)
    LOGGER.info(product_id)

    item_restored = product_sql.product_restore(product_id, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("< Назад", callback_data="PRODUCT_START"),
            ]
        ]
    ) 

    reply_text = "Объявление восстановлено. Вы снова будете получать заявки."

    await query.edit_message_text(reply_text, reply_markup=menu)

PRODUCT_TYPE, NAME, DESCRIPTION, IMAGE, CATEGORY, CONFIRMATION = range(6)

# main
add_product = ConversationHandler(
    entry_points=[
            MessageHandler(filters.TEXT & filters.Regex('Купить/Продать') & filters.ChatType.PRIVATE, new_product),
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
        IMAGE: [
            MessageHandler(filters.PHOTO, image),

            MessageHandler(filters.Regex('^Пропустить$'), skip_image),
            CommandHandler("skip", skip_image),
        ],
        CATEGORY: [MessageHandler(~filters.COMMAND & filters.TEXT, category)],
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
    edit_item_has_restored,
]

application.add_handlers([add_product, product_inform_seller] + edit_handlers)
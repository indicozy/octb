from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler
from decouple import config
from nu_bot.modules.sql import base as db
from nu_bot import LOGGER
from nu_bot.modules.helpers.base import generate_post

# storage
import os

# TODO add redis
product_preps = {}

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

    categories = db.get_all_categories()
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

        product_new_id = db.add_product(message_id=message.id, is_selling=product_preps[user.id]['is_selling'], name=product_preps[user.id]['name'], description=product_preps[user.id]['description'],
                       seller_tg_id=user.id, category_name=product_preps[user.id]['category'], has_image= product_preps[user.id]['photo_location'] != None)

        await update.message.reply_text("Продукт добавлен!")

        if product_preps[user.id]['photo_location']:
            os.rename(product_preps[user.id]['photo_location'], f'{storage_folder}{product_new_id}.jpg')
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

    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("text of %s: %s", user.first_name, update.message.text)

    items = db.get_products_from_tg_user(user.id)

    menu = InlineKeyboardMarkup(generate_menu([InlineKeyboardButton(item.name[:20], callback_data=str(item.id)) for item, index in zip(items, range(len(items)))])) 

    await update.message.reply_text("Ваши Объявления:", reply_markup=menu)
    return ITEM_MENU

async def item_menu_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    query = update.callback_query
    await query.answer()

    user = query.message.chat
    text = query.data
    LOGGER.info("callback of %s: %s", user.id, text)

    item = db.get_product_by_id(text, user.id) # TODO add verification of callback

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Удалить Пост", callback_data=f"ARCHIVE-{text}"),
            ],
            [
                InlineKeyboardButton("Объявление Продано", callback_data=f"SOLD-{text}"),
            ],
            [
                InlineKeyboardButton("< Назад", callback_data="BACK"),
            ]
        ]
    ) 

    await query.edit_message_text(
        generate_post(headline=item.name, text=item.description, hashtags=[item.is_selling, item.category]), reply_markup=menu)
    return ITEM_MENU_ACTIONS

PRODUCT_TYPE, NAME, DESCRIPTION, IMAGE, CATEGORY, CONFIRMATION = range(6)

# main
add_product = ConversationHandler(
    entry_points=[
            MessageHandler(filters.TEXT & filters.Regex('Купить/Продать') & filters.ChatType.PRIVATE, new_product),
            CommandHandler("new_item", new_product),
        ],
    states={
        PRODUCT_TYPE: [MessageHandler(filters.TEXT, product_type)],
        NAME: [MessageHandler(filters.TEXT, name)],
        DESCRIPTION: [
            MessageHandler(filters.TEXT, description),

            MessageHandler(filters.Regex('^Пропустить$'), skip_description),
            CommandHandler("skip", skip_description),
            ],
        IMAGE: [
            MessageHandler(filters.PHOTO, image),

            MessageHandler(filters.Regex('^Пропустить$'), skip_image),
            CommandHandler("skip", skip_image),
        ],
        CATEGORY: [MessageHandler(filters.TEXT, category)],
        CONFIRMATION: [MessageHandler(filters.TEXT, confirmation)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

ITEM_MENU, ITEM_ARCHIVE, ITEM_MENU_ACTIONS, ITEM_BACK = range(4)

edit_handler = ConversationHandler(
        entry_points=[
            CommandHandler("my_items", item_menu_select),
            MessageHandler(filters.Regex('^Мои Объявления$'), item_menu_select),
            ],
        states={
            ITEM_MENU: [
                CallbackQueryHandler(item_menu_get_id),
            ],
            ITEM_MENU_ACTIONS: [
                # CallbackQueryHandler(item_archive),
                # CallbackQueryHandler(item_sold),
                CallbackQueryHandler(item_menu_select),
            ],
            # ITEM_ARCHIVE: [
            #     CallbackQueryHandler(item_menu_archive, pattern="^" + str(ITEM_ARCHIVE) + "$"),
            # ],
            # ITEM_SOLD: [
            #     CallbackQueryHandler(item_menu_edit, pattern="^" + str(ITEM_MENU_EDIT_MENU) + "$"),
            # ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler, CallbackQueryHandler

import octb.modules.sql.dating as sql
from octb import LOGGER
from octb.modules.helpers.product import generate_post_product
from octb.modules.helpers.base import generate_post, generate_menu

from octb import application

import datetime

# storage
import os

# TODO add redis
dating_preps = {}
categories = {
    "study-buddy": "Study-buddy",
    "romance": "Романтика",
    "friend": "Друзья",
    "Sport": "Спорт",
    "hobbies": "Хобби",
    "roomate": "Руммейты"
}

dating_status = {}
def dating_status_restore():
    dating_status = {}

def gender_conf(gender):
    if gender == True:
        return "Мужчина"
    elif gender == False:
        return "Женщина"
    else:
        return "Другое"

__mod_name__ = "dating"

from decouple import config
# env
STORAGE=config('STORAGE')

async def new_dating_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    dating_preps[user.id] = {}
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "Имя"
    )

    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    dating_preps[user.id]['name'] = update.message.text
    
    await update.message.reply_text(
        "Gender?"
        "Send /cancel to stop talking to me.\n\n"
    )

    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text.lower()
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    if user_text == "мужчина":
        dating_preps[user.id]['gender'] = True
    elif user_text == "женщина":
        dating_preps[user.id]['gender'] = False
    elif user_text == "другое":
        dating_preps[user.id]['gender'] = None
    else:
        await update.message.reply_text(
            "Gender?"
            "Send /cancel to stop talking to me.\n\n"
        )
        return GENDER
    
    await update.message.reply_text(
        "Gender you like?"
        "Send /cancel to stop talking to me.\n\n"
    )

    return INTEREST_GENDER

async def interest_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text.lower()
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    if user_text == "мужчины":
        dating_preps[user.id]['interest_gender'] = True
    elif user_text == "женщины":
        dating_preps[user.id]['interest_gender'] = False
    elif user_text == "все":
        dating_preps[user.id]['interest_gender'] = None
    else:
        await update.message.reply_text(
            "Gender you like?"
            "Send /cancel to stop talking to me.\n\n"
        )
        return INTEREST_GENDER
    
    await update.message.reply_text(
        "Are you in campus?"
        "Send /cancel to stop talking to me.\n\n"
    )

    return IS_ON_CAMPUS

async def is_on_campus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    user_text = user_text.lower()
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    if user_text == "да":
        dating_preps[user.id]['is_on_campus'] = True
        dating_preps[user.id]['location'] = "Кампус".capitalize()
        await update.message.reply_text(
            "Your age?"
            "Send /cancel to stop talking to me.\n\n"
        )
        return AGE
    elif user_text == "нет":
        dating_preps[user.id]['is_on_campus'] = False
        await update.message.reply_text(
            "Your location?"
            "Send /cancel to stop talking to me.\n\n"
        )

        return LOCATION
    else:
        await update.message.reply_text(
            "Are you in campus?"
            "Send /cancel to stop talking to me.\n\n"
        )
        return INTEREST_GENDER

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    user_text = user_text.capitalize()
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)

    dating_preps[user.id]['location'] = user_text
    await update.message.reply_text(
        "Your age?"
        "Send /cancel to stop talking to me.\n\n"
    )
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    if not user_text.isdigit():
        await update.message.reply_text(
            "Your age?"
            "Send /cancel to stop talking to me.\n\n"
        )
        return AGE

    dating_preps[user.id]['age'] = int(user_text)
    await update.message.reply_text(
        "Description?"
        "Send /cancel to stop talking to me.\n\n"
    )
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)

    dating_preps[user.id]['description'] = user_text
    await update.message.reply_text(
        "Send image"
        "Send /cancel to stop talking to me.\n\n"
    )
    return IMAGE

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user

    file_id = update.message.photo[-1].file_id
    newFile = await context.bot.getFile(file_id)

    storage_location = f'{STORAGE}/photos/temp/dating/{user.id}.jpg'

    await newFile.download(storage_location)
    
    LOGGER.info("name of %s: %s", user.first_name, update.message.text)
    dating_preps[user.id]['photo_location'] = storage_location

    text = generate_post(dating_preps[user.id]['name'], dating_preps[user.id]['description'], ["ваши_категории"], args={"Возраст" : dating_preps[user.id]['age'],
                                                                                                                   "Гендер": gender_conf(dating_preps[user.id]['gender']),
                                                                                                                    "Город": dating_preps[user.id]['location'],
                                                                                                                   })

    text += "\n\ny/n?"

    await update.message.reply_text(text)

    return CONFIRMATION

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    dating_preps[user.id]['photo_location'] = None
    text = generate_post(dating_preps[user.id]['name'], dating_preps[user.id]['description'], [f"ваши_категории"], args={"Возраст" : dating_preps[user.id]['age'],
                                                                                                                   "Гендер": gender_conf(dating_preps[user.id]['gender']),
                                                                                                                    "Город": dating_preps[user.id]['location'],
                                                                                                                   })

    text += "\n\ny/n?"
    await update.message.reply_text(text)

    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    def marketplace_text(name, description, product_type, category):
        return f"""#{product_type.value.lower()} #{category.lower()} \n{name}\n\n{description}\n\n @{MARKETPLACE_CHAT_ACCOUNT}"""

    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    user_text = update.message.text
    user_text = user_text.lower()
    LOGGER.info("text of %s: %s", user.first_name, update.message.text)

    if user_text in ['N', 'n', "Нет", "нет"]:
        await update.message.reply_text(
            "Вы вернулись в главный экран"
        )
        return ConversationHandler.END

    elif user_text in ['y', 'да']:

        storage_folder = f'{STORAGE}/photos/dating/'

        if dating_preps[user.id]['photo_location']:
            os.rename(dating_preps[user.id]['photo_location'], f'{storage_folder}{user.id}.jpg')
            # photo_location = storage_folder

        user_id = user.id
        name = dating_preps[user.id]['name']
        gender = dating_preps[user.id]['gender']
        interest_gender = dating_preps[user.id]['interest_gender']
        location = dating_preps[user.id]['location']
        age = dating_preps[user.id]['age']
        has_image = bool(dating_preps[user.id]['photo_location'])
        is_on_campus = dating_preps[user.id]['is_on_campus']
        description = dating_preps[user.id]['description']

        dating_user_new = sql.add_dating_user(user_id, name, gender, interest_gender, location, age, has_image, is_on_campus=is_on_campus, description=description)

        user_categories = sql.get_dating_category_by_user_id(user.id)
        # ✅
        menu_items = []
        for key, value in categories.items():
            inserted = False
            for category in user_categories:
                if category.name == key and not inserted:
                    inserted = True
                    menu_items.append(InlineKeyboardButton(f"✅{value}", callback_data=f"DATING_CATEGORY_TOGGLE_{key}"))
            if not inserted:
                menu_items.append(InlineKeyboardButton(f"{value}", callback_data=f"DATING_CATEGORY_TOGGLE_{key}"))
                
        menu = InlineKeyboardMarkup(generate_menu(menu_items))
        await update.message.reply_text("Вы добавлены!\nВыберите категории, в которых вы хотите найти партнера", reply_markup=menu)
        
        try:
            dating_preps.pop(user.id) # TODO try except
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
        dating_preps.pop(user.id) # TODO try except
    except:
        pass

    return ConversationHandler.END

async def dating_category_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    user = query.from_user
    text = query.data
    
    LOGGER.info("text of %s: %s", user.first_name, text)

    category_key = text.replace("DATING_CATEGORY_TOGGLE_", "")
    if category_key not in categories.keys():
        await query.answer()
        return

    category_toggle = sql.toggle_dating_category(user.id, category_key)
    user_categories = sql.get_dating_category_by_user_id(user.id)
    menu_items = []
    for key, value in categories.items():
        inserted = False
        for category in user_categories:
            if category.name == key and not inserted:
                inserted = True
                menu_items.append(InlineKeyboardButton(f"✅{value}", callback_data=f"DATING_CATEGORY_TOGGLE_{key}"))
        if not inserted:
            menu_items.append(InlineKeyboardButton(f"{value}", callback_data=f"DATING_CATEGORY_TOGGLE_{key}"))
            
    menu = InlineKeyboardMarkup(generate_menu(menu_items))

    await query.edit_message_text(
        "Ваши категории:", reply_markup=menu
        )

NAME, GENDER, INTEREST_GENDER, IS_ON_CAMPUS, LOCATION, AGE, DESCRIPTION, IMAGE, CONFIRMATION = range(9)

# main
add_dating_user = ConversationHandler(
    entry_points=[
            CommandHandler("meet", new_dating_user, filters=filters.ChatType.PRIVATE),
        ],
    states={
        NAME: [
            MessageHandler(~filters.COMMAND & filters.TEXT, name)
            ],
        GENDER: [
            MessageHandler(~filters.COMMAND & filters.TEXT, gender)
            ],
        INTEREST_GENDER: [
                MessageHandler(~filters.COMMAND & filters.TEXT, interest_gender),
            ],
        IS_ON_CAMPUS: [
                MessageHandler(~filters.COMMAND & filters.TEXT, is_on_campus),
        ],
        LOCATION: [
            MessageHandler(~filters.COMMAND & filters.TEXT, location),
            ],
        AGE: [
            MessageHandler(~filters.COMMAND & filters.TEXT, age)
            ],
        DESCRIPTION: [
            MessageHandler(~filters.COMMAND & filters.TEXT, description)
            ],
        IMAGE: [
            MessageHandler(filters.PHOTO, image),

            MessageHandler(filters.Regex('^Пропустить$'), skip_image),
            CommandHandler("skip", skip_image),
            ],
        CONFIRMATION: [
            MessageHandler(~filters.COMMAND & filters.TEXT, confirmation)
            ],
    },
        # CATEGORIES: [MessageHandler(~filters.COMMAND & filters.TEXT, confirmation)],
    fallbacks=[CommandHandler("cancel", cancel)],
)

dating_category_toggle_handler = CallbackQueryHandler(dating_category_toggle, pattern="^" + "DATING_CATEGORY_TOGGLE_")

STATUS, ENVELOPE = range(2)

add_dating_user = ConversationHandler(
    entry_points=[
            CommandHandler("search", new_dating_user, filters=filters.ChatType.PRIVATE),
        ],
    states={
        STATUS: [
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^❤️$'), like),
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^👎️$'), dislike),
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^✉️$'), envelope),
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^💤️$'), sleep),
            ],
        ENVELOPE: [
            MessageHandler(filters.Regex('^Отмена$'), skip_envelope),
            MessageHandler(filters.Regex('^Отмена$'), send_envelope),
            CommandHandler("skip", skip_envelope),
            ],
    },
        # CATEGORIES: [MessageHandler(~filters.COMMAND & filters.TEXT, confirmation)],
    fallbacks=[CommandHandler("cancel", cancel)],
)

# TODO add handlers for reaction
# TODO add matches and rejects sql

dating_category_handlers = [
    dating_category_toggle_handler,
]

application.add_handlers([add_dating_user] + dating_category_handlers)
application.job_queue.run_daily(dating_status_restore, datetime.time(hour=5, minute=0))
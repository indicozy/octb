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
    "study_buddy": "Study-buddy",
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

    menu = ReplyKeyboardMarkup([
        [
            'Мужчина',
        ],
        [
            'Женщина',
        ],
        [
            'Другое',
        ],
    ], one_time_keyboard=True)
    
    await update.message.reply_text(
        "Gender?"
        "Send /cancel to stop talking to me.\n\n",
        reply_markup=menu
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
        menu = ReplyKeyboardMarkup([
            [
                'Мужчина',
            ],
            [
                'Женщина',
            ],
            [
                'Другое',
            ],
        ], one_time_keyboard=True)
        await update.message.reply_text(
            "Gender?"
            "Send /cancel to stop talking to me.\n\n",
            reply_markup=menu
        )
        return GENDER

    menu = ReplyKeyboardMarkup([
        [
            'Мужчины',
        ],
        [
            'Женщины',
        ],
        [
            'Все',
        ],
    ], one_time_keyboard=True)
    
    await update.message.reply_text(
        "Gender you like?"
        "Send /cancel to stop talking to me.\n\n",
        reply_markup=menu
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
        menu = ReplyKeyboardMarkup([
            [
                'Мужчины',
            ],
            [
                'Женщины',
            ],
            [
                'Все',
            ],
        ], one_time_keyboard=True)
        await update.message.reply_text(
            "Gender you like?"
            "Send /cancel to stop talking to me.\n\n",
            reply_markup=menu
        )
        return INTEREST_GENDER

    menu = ReplyKeyboardMarkup([
        [
            'Да', 'Нет'
        ],
    ], one_time_keyboard=True)
    
    await update.message.reply_text(
        "Are you in campus?"
        "Send /cancel to stop talking to me.\n\n",
        reply_markup=menu
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
        menu = ReplyKeyboardMarkup([
            [
                'Да', 'Нет'
            ],
        ], one_time_keyboard=True)
        await update.message.reply_text(
            "Are you in campus?"
            "Send /cancel to stop talking to me.\n\n",
            reply_markup=menu
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

async def show_interests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query

        user = update.callback_query.from_user
        text = query.data
    else:
        user = update.message.from_user
        text = update.message.text
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
    await context.bot.send_message(chat_id=user.id, text="Выберите категории, в которых вы хотите найти партнера и вы можете начать искать партнера", reply_markup=menu)

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

        await show_interests(update, context)
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

def get_interests(user_id):
    if not (user_id in dating_status and 'interests' in dating_status[user_id]):
        if not dating_status[user_id]:
            dating_status[user_id] = {}
        dating_status[user_id]['interests'] = sql.get_user_categories(user_id)
    return dating_status[user_id]['interests']

def generate_post_partner(dating_partner, categories):
    return generate_post(f"{dating_partner.name} - {dating_partner.location}", dating_partner.description, categories, args={"Возраст" : dating_partner.age,
                                                                                                        "Гендер": dating_partner.gender,
                                                                                                        "Город": dating_partner.location,
                                                                                                        })

async def find_next_partner(update, user_id):
    if not (user_id in dating_status and 'last_partner_id' in dating_status[user_id]):
        dating_status[user_id] = {}
        dating_status[user_id]['last_partner_id'] = 0
    dating_user = sql.get_dating_user_by_id(user_id)
    if not dating_user:
        await update.message.reply_text("Вы не добавлены в партнеры")
        return ConversationHandler.END 
    
    interests = get_interests(user_id)
    print(interests)
    print(user_id)
    sql_data = sql.get_potential_partner_by_interest(user_id, dating_status[user_id]['last_partner_id'], interests)
    print(sql_data)
    if not sql_data:
        await update.message.reply_text("На сегодня все, Вы вышли на главное меню")
        return ConversationHandler.END
    dating_partner = sql_data[0][0]
    categories = [category.name for _, category in [row for row in sql_data]]
    categories_merge = list(set(categories).intersection(interests))
    print(dating_partner)
    print(categories)

    dating_status[user_id]['last_partner_id'] = dating_partner.user_id
    text = generate_post_partner(dating_partner, categories_merge)
    menu = ReplyKeyboardMarkup([
        [
            'like',
        ],
        [
            'dislike',
        ],
        [
            'sleep',
        ],
    ], one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=menu)
    return STATUS

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    response = await find_next_partner(update, user.id)
    print(response)
    return response

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    menu = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"like", callback_data=f"DATING_RESPONSE_LIKE_{user.id}"),
            InlineKeyboardButton(f"dislike", callback_data=f"DATING_RESPONSE_DISLIKE_{user.id}")
         ],
    ])
    
    LOGGER.info("User %s did not send image.", user.first_name)
    text = "Кто-то тебя лайкнул!\n\n"
    dating_partner = sql.get_dating_user_by_id(user.id)
    categories = sql.get_user_categories(user.id)
    text += generate_post_partner(dating_partner, categories=categories)
    await context.bot.send_message(text=text,
                                   chat_id=dating_status[user.id]['last_partner_id'],
                                   reply_markup=menu
                                   )
    response = await find_next_partner(update, user.id)
    return response

async def dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    response = await find_next_partner(update, user.id)
    return response

async def sleep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    LOGGER.info("User %s did not send image.", user.first_name)
    text = "Вы вышли из поисковика"
    await update.message.reply_text(text)
    return ConversationHandler.END

async def dating_response_like(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    async def send_message_like(user_id, user_recipient):
        dating_user_liked = sql.get_dating_user_by_id(user_id)
        dating_category_liked = sql.get_dating_category_by_user_id(user_id)
        dating_category_liked = [category.name for category in dating_category_liked]
        menu_liked = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"Профиль", url=f"tg://user?id={user_id}")
            ],
        ])
        await context.bot.send_message(chat_id=user_recipient, text="У вас взаимный лайк!\n\n" + generate_post_partner(dating_user_liked, dating_category_liked),
                                    reply_markup=menu_liked)
    query = update.callback_query
    print("lmao")

    user = query.from_user
    text = query.data
    
    await query.answer()
    LOGGER.info("text of %s: %s", user.first_name, text)

    user_liked = int(text.replace("DATING_RESPONSE_LIKE_", ""))
    await send_message_like(user_liked, user.id)
    await send_message_like(user.id, user_liked)
    sql.add_match(user_liked, user.id)

async def dating_response_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    user = query.from_user
    text = query.data
    
    await query.answer()
    LOGGER.info("text of %s: %s", user.first_name, text)

    user_liked = int(text.replace("DATING_RESPONSE_LIKE_", ""))
    sql.add_reject(user_liked, user.id)

STATUS, ENVELOPE = range(2)

search_date = ConversationHandler(
    entry_points=[
            CommandHandler("search", search, filters=filters.ChatType.PRIVATE),
        ],
    states={
        STATUS: [
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^like$'), like),
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^dislike$'), dislike),
            # MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^✉️$'), envelope),
            MessageHandler(~filters.COMMAND & filters.TEXT & filters.Regex('^sleep$'), sleep),
            ],
        # ENVELOPE: [
        #     MessageHandler(filters.Regex('^Отмена$'), skip_envelope),
        #     MessageHandler(~filters.COMMAND & filters.TEXT, send_envelope),
        #     CommandHandler("skip", skip_envelope),
        #     ],
    },
        # CATEGORIES: [MessageHandler(~filters.COMMAND & filters.TEXT, confirmation)],
    fallbacks=[CommandHandler("cancel", cancel)],
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

# TODO add handlers for reaction
# TODO add matches and rejects sql

show_interests_handler = CommandHandler("interests", show_interests, filters=filters.ChatType.PRIVATE)

dating_category_toggle_handler = CallbackQueryHandler(dating_category_toggle, pattern="^" + "DATING_CATEGORY_TOGGLE_")

dating_response_like_handler = CallbackQueryHandler(dating_response_like, pattern="^" + "DATING_RESPONSE_LIKE_")
dating_response_dislike_handler = CallbackQueryHandler(dating_response_dislike, pattern="^" + "DATING_RESPONSE_LIKE_")


application.add_handlers([search_date, add_dating_user, show_interests_handler, dating_category_toggle_handler, dating_response_like_handler, dating_response_dislike_handler])
application.job_queue.run_daily(dating_status_restore, datetime.time(hour=5, minute=0))
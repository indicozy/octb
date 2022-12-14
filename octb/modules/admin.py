from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, ConversationHandler, MessageHandler
import time

import octb.modules.sql as sql
import asyncio

from octb import application, LOGGER

__mod_name__ = "admin"

from decouple import config
STORAGE=config('STORAGE')

from decouple import config
SUPERADMIN_ID=int(config('SUPERADMIN_ID'))

MAX_COROUTINES = 5

async def stats(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text

    if user.id != SUPERADMIN_ID:
        await update.message.reply_text("У вас нет прав")
        return
    
    users_count = sql.user.count_users()
    products_count = sql.product.count_products()
    bought_items_count = sql.product.count_product_buyers()
    dating_users_count = sql.dating.count_dating_users()
    dating_matches_count = sql.dating.count_dating_matches()
    dating_users_males_count = sql.dating.count_dating_users_gender(True)
    dating_users_females_count = sql.dating.count_dating_users_gender(False)

    seller_stats = {}
    seller_names = {}
    sales_arr = []
    product_sold_by_seller = sql.product.get_products_by_seller()

    for seller, product, buyer in product_sold_by_seller:
        try: 
            sales_arr.append([int(s) for s in product.price.split() if s.isdigit()][0])
        except:
            pass

        if seller.name and seller.name not in seller_stats:
            seller_names[seller.user_id] = seller.name

        if seller.user_id not in seller_stats:
            seller_stats[seller.user_id] = 1
        else:
            seller_stats[seller.user_id] += 1
    sales = sum(sales_arr)

    # print(sales_arr)

    response = ""
    response += f"Users: {users_count}\n"
    response += f"Product: {products_count}\n"
    response += f"Bought_items: {bought_items_count}\n"
    response += f"Sales: {sales}тг\n"
    response += f"Dating_users: {dating_users_count}\n"
    response += f"Dating_users_males: {dating_users_males_count}\n"
    response += f"Dating_users_females: {dating_users_females_count}\n"
    response += f"Dating_matches: {dating_matches_count}\n"

    response += "\n\nBest sellers:\n" # TODO not tested
    for seller_id, count in seller_stats.items():
        if seller_id in seller_names:
            response+= f"{seller_names[seller_id]}: {count}\n"
        else:
            response+= f"{seller_id}: {count}\n"

    await update.message.reply_text(text=response)

async def sendall(update: Update, context:ContextTypes.DEFAULT_TYPE):
    async def gather_with_concurrency(n, *tasks):
        semaphore = asyncio.Semaphore(n)
        async def sem_task(task):
            async with semaphore:
                return await task
        return await asyncio.gather(*(sem_task(task) for task in tasks))
    
    async def send_message(user_id, text, file=None, is_video=False):
        try: 
            if file and is_video:
                await context.bot.send_video(video=file, chat_id=user_id, caption=text)
            elif file and not is_video:
                await context.bot.send_photo(photo=file, chat_id=user_id, caption=text)
            else:
                await context.bot.send_message(chat_id=user_id, text=text)
            return True
        except Exception as e:
            LOGGER.info(str(e))
            return False

    user = update.message.from_user
    user_text = update.message.text

    message_replied = update.message.reply_to_message

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
    
    users = sql.user.get_users_all()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Отправляем сообщение:\n\n{text}\n\n{len(users)} пользователям...")
    start_time = time.time()
    if message_replied and message_replied.photo:
        file_id = message_replied.photo[-1].file_id
        newFile = await context.bot.getFile(file_id)
        storage_location = f'{STORAGE}/photos/temp/admin/{user.id}.jpg'
        await newFile.download(storage_location)
        is_sent_list = await gather_with_concurrency(MAX_COROUTINES, *[send_message(user.user_id, text, file=open(storage_location, 'rb')) for user in users]) # TODO check if it won't break up
    elif message_replied and message_replied.video:
        file_id = message_replied.video.file_id
        newFile = await context.bot.getFile(file_id)
        storage_location = f'{STORAGE}/photos/temp/admin/{user.id}.mp4'
        await newFile.download(storage_location)
        is_sent_list = await gather_with_concurrency(MAX_COROUTINES, *[send_message(user.user_id, text, file=open(storage_location, 'rb'), is_video=True) for user in users]) # TODO check if it won't break up
    else:
        is_sent_list = await gather_with_concurrency(MAX_COROUTINES, *[send_message(user.user_id, text) for user in users]) # TODO check if it won't break up

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Сообщение отправлено:\n\n{text}\n\n{sum(is_sent_list)} пользователей получили, {len(is_sent_list) - sum(is_sent_list)} пользователей  НЕ получили сообщения\n\nОтправлено за {time.time() - start_time} секунд")

# handlers
sendall_handler = CommandHandler('sendall', sendall, filters=filters.ChatType.PRIVATE)
stats_handler = CommandHandler('stats', stats, filters=filters.ChatType.PRIVATE)

application.add_handlers([sendall_handler, stats_handler])
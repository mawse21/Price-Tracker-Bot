import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackQueryHandler
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scraper import get_info
from config import TOKEN
from handlers import *

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

async def schedule(app: ApplicationBuilder):
    loop = asyncio.get_running_loop()
    scheduler = AsyncIOScheduler(event_loop=loop)
    app.bot_data['scheduler'] = scheduler
    scheduler.start()



if __name__ == "__main__":

    app = ApplicationBuilder().token(TOKEN).post_init(schedule).build()

    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('show', show))
    app.add_handler(CommandHandler("remove", remove))

    app.add_handler(CallbackQueryHandler(remove_callback, pattern="^remove:"))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("polling....")
    app.run_polling()

    conn.close()
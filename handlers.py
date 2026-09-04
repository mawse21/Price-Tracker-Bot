import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
import sqlite3
from scraper import get_info, clean_price

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

async def check_price(chat_id, bot, url):
    info = get_info(url)


    await bot.send_message(
            chat_id=chat_id, 
            text=f"🚨The item {info["name"]} is now {info["price"]} ."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scheduler = context.bot_data['scheduler']
    url = update.message.text
    info = get_info(url)
    if info["price"]:
        await update.message.reply_text(f"Product added successfully!\nthe price now is {info["price"]}.")
        chat_id = update.effective_chat.id
        info["price"] = clean_price(info["price"])

        cursor.execute("INSERT INTO products (name, url, current_price, last_checked, store) VALUES (?, ?, ?, ?, ?)",
                        (info["name"], url, info["price"], info["time"], info["store"]))

        user_id = cursor.execute("SELECT id FROM users WHERE telegram_id == ?", (update.effective_user.id,)).fetchone()
        user_id = int(user_id[0])
        product_id = cursor.execute("SELECT id FROM products WHERE url == ?", (url,)).fetchone()
        product_id = int(product_id[0])

        cursor.execute("INSERT INTO user_products (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        conn.commit()
        scheduler.add_job(
            check_price,
            trigger="interval",
            minutes=60,
            kwargs={'chat_id':chat_id, 'bot':context.bot, 'url':url},
            id=f"{product_id}"
            )
    else:
        await update.message.reply_text("Please provide a valid product link from Jumia or Noon.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi, I am a price monitor bot to keep you updated with product price.\n Press start to add a product!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Start by adding a product link from: Jumia/Noon.")

    user = update.effective_user
    try:
        cursor.execute("INSERT INTO users (telegram_id, username) VALUES (?, ?)", (user.id, user.username))
        conn.commit()
    except:
        pass


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products_string = "Your current products:\n"
    user_id = cursor.execute("SELECT id FROM users WHERE telegram_id == ?", (update.effective_user.id,)).fetchone()
    user_id = int(user_id[0])

    products = cursor.execute("SELECT name FROM products WHERE id IN (SELECT product_id FROM user_products WHERE user_id == ?)", (user_id,)).fetchall()
    if not products:
        await update.message.reply_text("You don't have any products.")
        return
    for index, product in enumerate(products, start=1):
        products_string += f"{index}.{product[0]}\n"
    await update.message.reply_text(products_string)

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = cursor.execute("SELECT id FROM users WHERE telegram_id == ?", (update.effective_user.id,)).fetchone()
    user_id = int(user_id[0])

    products = cursor.execute("SELECT id, name FROM products WHERE id IN (SELECT product_id FROM user_products WHERE user_id == ?)", (user_id,)).fetchall()

    if not products:
        await update.message.reply_text("You don't have any products.")
        return

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"remove:{product_id}")]
        for product_id, name in products
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select a product to remove:",
        reply_markup=reply_markup
    )

async def remove_callback(update, context):
    scheduler = context.bot_data['scheduler']

    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    user_id = cursor.execute("SELECT id FROM users WHERE telegram_id == ?", (update.effective_user.id,)).fetchone()
    user_id = int(user_id[0])
    cursor.execute("DELETE FROM user_products WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    try:
        scheduler.remove_job(product_id)
    except:
        pass
    await query.edit_message_text("✅ Product removed.")
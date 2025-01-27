from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import sqlite3
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Make sure to set the BOT_TOKEN in your environment variables

# User states for conversation
user_data = {}

# Initialize database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        stream TEXT,  -- Allow NULL for this field
        course TEXT NOT NULL,
        college_type TEXT NOT NULL,
        roll_number TEXT NOT NULL,
        sport TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Save to database
def save_to_db(user_id):
    data = user_data[user_id]
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO registrations (user_id, name, phone, stream, course, college_type, roll_number, sport)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            data["name"],
            data["phone"],
            data.get("stream"),  # Safely get stream or use None if not present
            data["course"],
            data["college_type"],
            data["roll_number"],
            data["sport"],
        ),
    )
    conn.commit()
    conn.close()

# Flask web server to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome to Sathaye College Sports Registration! ⚽\n\nPlease enter your *full name* to begin registration:",
        parse_mode="Markdown",
    )
    user_data[update.message.from_user.id] = {"step": "name"}


# Handle user responses
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Type /start to begin registration.")
        return

    step = user_data[user_id].get("step")

    if step == "name":
        user_data[user_id]["name"] = text
        user_data[user_id]["step"] = "phone"
        await update.message.reply_text(
            "📱 Please enter your *phone number*:",
            parse_mode="Markdown",
        )

    elif step == "phone":
        user_data[user_id]["phone"] = text
        user_data[user_id]["step"] = "college_type"
        keyboard = [
            [InlineKeyboardButton("Junior College", callback_data="Junior College")],
            [InlineKeyboardButton("Degree College", callback_data="Degree College")],
            [InlineKeyboardButton("Masters", callback_data="Masters")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🎓 Select your *college type*:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif step == "roll_number":
        user_data[user_id]["roll_number"] = text
        user_data[user_id]["step"] = "sport"
        keyboard = [
            [InlineKeyboardButton("⚽ Football", callback_data="Football"),
             InlineKeyboardButton("🏀 Basketball", callback_data="Basketball")],
            [InlineKeyboardButton("🏆 Athletics", callback_data="Athletics"),
             InlineKeyboardButton("🏈 Cricket", callback_data="Cricket")],
            [InlineKeyboardButton("🎮 Chess", callback_data="Chess"),
             InlineKeyboardButton("⛳ Badminton", callback_data="Badminton")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🏃‍♂️ Select your *preferred sport*:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


# Handle button selections
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.message.reply_text("Type /start to begin registration.")
        return

    step = user_data[user_id].get("step")

    if step == "college_type":
        user_data[user_id]["college_type"] = query.data
        if query.data == "Junior College":
            user_data[user_id]["step"] = "stream"
            keyboard = [
                [InlineKeyboardButton("Science", callback_data="Science"),
                 InlineKeyboardButton("Commerce", callback_data="Commerce")],
                [InlineKeyboardButton("Arts", callback_data="Arts")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "📚 Select your *stream*:",
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
        elif query.data == "Degree College":
            user_data[user_id]["step"] = "course"
            keyboard = [
                [InlineKeyboardButton("B.Sc.", callback_data="B.Sc."),
                 InlineKeyboardButton("B.Com.", callback_data="B.Com.")],
                [InlineKeyboardButton("B.A.", callback_data="B.A."),
                 InlineKeyboardButton("BMS", callback_data="BMS")],
                [InlineKeyboardButton("B.Sc. IT", callback_data="B.Sc. IT"),
                 InlineKeyboardButton("Other", callback_data="Other")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "🎓 Select your *course*:",
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
        elif query.data == "Masters":
            user_data[user_id]["step"] = "course"
            keyboard = [
                [InlineKeyboardButton("M.Sc.", callback_data="M.Sc."),
                 InlineKeyboardButton("M.Com.", callback_data="M.Com.")],
                [InlineKeyboardButton("M.A.", callback_data="M.A."),
                 InlineKeyboardButton("Other", callback_data="Other")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "🎓 Select your *course*:",
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )

    elif step == "stream":
        user_data[user_id]["stream"] = query.data
        user_data[user_id]["step"] = "course"
        keyboard = [
            [InlineKeyboardButton("FYJC", callback_data="FYJC"),
             InlineKeyboardButton("SYJC", callback_data="SYJC")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "🎓 Select your *course*:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif step == "course":
        if query.data == "Other":
            user_data[user_id]["step"] = "specify_course"
            await query.message.reply_text(
                "🔹 Please specify your course:",
                parse_mode="Markdown",
            )
        else:
            user_data[user_id]["course"] = query.data
            user_data[user_id]["step"] = "roll_number"
            await query.message.reply_text(
                "🔹 Enter your *roll number*:",
                parse_mode="Markdown",
            )

    elif step == "sport":
        user_data[user_id]["sport"] = query.data
        save_to_db(user_id)
        await query.message.reply_text(
            "🎉 Registration complete! Thank you for registering for Sathaye College Sports. 🏆",
            parse_mode="Markdown",
        )
        del user_data[user_id]

    await query.answer()


# Main function
def main():
    init_db()
    keep_alive()  # Start the web server

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == "__main__":
    main()

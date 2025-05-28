import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Sample quiz questions
standard_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Paris", "Rome", "Madrid"],
        "correct_option_id": 1
    }
]

anonymous_questions = [
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "correct_option_id": 1
    }
]

# /start command with buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Standard Quiz", callback_data='standard')],
        [InlineKeyboardButton("Anonymous Quiz", callback_data='anonymous')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a quiz mode:", reply_markup=reply_markup)

# Callback button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "standard":
        await send_quiz(query, context, is_anonymous=False)
    elif query.data == "anonymous":
        await send_quiz(query, context, is_anonymous=True)

# Shared quiz sending function
async def send_quiz(query, context: ContextTypes.DEFAULT_TYPE, is_anonymous: bool):
    quiz_list = anonymous_questions if is_anonymous else standard_questions
    quiz = quiz_list[0]

    await context.bot.send_poll(
        chat_id=query.message.chat_id,
        question=quiz["question"],
        options=quiz["options"],
        type="quiz",
        correct_option_id=quiz["correct_option_id"],
        is_anonymous=is_anonymous
    )

# Error logging
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)

# Main application
def main():
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN environment variable not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

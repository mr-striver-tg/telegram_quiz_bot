from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your bot token
TOKEN = "8014250953:AAHQ2YZs3IJHPgZCY-ZsHH9CSrYRf30ZK_kE"

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

# Start command with menu
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Standard Quiz", callback_data='standard')],
        [InlineKeyboardButton("Anonymous Quiz", callback_data='anonymous')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a quiz mode:", reply_markup=reply_markup)

# Handle button selection
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "standard":
        send_standard_quiz(query, context)
    elif query.data == "anonymous":
        send_anonymous_quiz(query, context)

# Standard quiz logic
def send_standard_quiz(query, context: CallbackContext):
    question = standard_questions[0]
    context.bot.send_poll(
        chat_id=query.message.chat_id,
        question=question["question"],
        options=question["options"],
        type='quiz',
        correct_option_id=question["correct_option_id"],
        is_anonymous=False
    )

# Anonymous quiz logic
def send_anonymous_quiz(query, context: CallbackContext):
    question = anonymous_questions[0]
    context.bot.send_poll(
        chat_id=query.message.chat_id,
        question=question["question"],
        options=question["options"],
        type='quiz',
        correct_option_id=question["correct_option_id"],
        is_anonymous=True
    )

# Error logging
def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

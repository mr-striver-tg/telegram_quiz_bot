import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# To track mode per user
user_mode = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Standard Quiz", callback_data='standard')],
        [InlineKeyboardButton("Anonymous Quiz", callback_data='anonymous')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a quiz mode:", reply_markup=reply_markup)

# Button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == "standard":
        user_mode[user_id] = False
        await query.edit_message_text("📘 Standard quiz mode activated.\nNow send your question in the proper format.")
    elif query.data == "anonymous":
        user_mode[user_id] = True
        await query.edit_message_text("🕵️ Anonymous quiz mode activated.\nNow send your question in the proper format.")

# Parse message and create quiz
async def handle_quiz_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    if not message or '✅' not in message or 'Ex:' not in message:
        return

    # Split question and explanation
    try:
        question_part, explanation = message.strip().rsplit("Ex:", 1)
    except ValueError:
        return

    lines = [line.strip("️ ").strip() for line in question_part.strip().split('\n') if line.strip()]
    
    if len(lines) < 5:
        return  # Expect at least: question + 4 options

    question = lines[0]
    options = []
    correct_option_id = None

    for idx, option in enumerate(lines[1:]):
        if "✅" in option:
            correct_option_id = idx
            option = option.replace("✅", "").strip()
        options.append(option)

    if correct_option_id is None or len(options) < 2 or len(options) > 10:
        await update.message.reply_text("❌ Invalid quiz format or missing correct answer.")
        return

    is_anonymous = user_mode.get(user_id, False)

    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        explanation=explanation.strip(),
        is_anonymous=is_anonymous
    )

# Main setup
def main():
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN environment variable not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_quiz_submission))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

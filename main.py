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

# User quiz mode tracker
user_mode = {}

# /start menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Standard Quiz", callback_data='standard')],
        [InlineKeyboardButton("Anonymous Quiz", callback_data='anonymous')],
    ]
    await update.message.reply_text("Choose a quiz mode:", reply_markup=InlineKeyboardMarkup(keyboard))

# Handle button click
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_mode[user_id] = query.data == "anonymous"
    await query.edit_message_text(
        "🟢 Anonymous mode ON." if user_mode[user_id] else "🔵 Standard mode ON.\nNow send your question(s)."
    )

# Handle quiz input (multiple questions supported)
async def handle_quiz_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_anonymous = user_mode.get(user_id, False)
    text = update.message.text

    if not text or '✅' not in text or 'Ex:' not in text:
        return

    # Split by each "Ex:" block, assuming one per quiz
    raw_blocks = re.split(r'\n?Ex:\s*', text.strip())
    quizzes = []

    for i in range(len(raw_blocks) - 1):  # last part is explanation of the last quiz
        quiz_text = raw_blocks[i].strip()
        explanation = raw_blocks[i + 1].split('\n')[0].strip()  # pick first line of explanation

        lines = [line.strip("️ ").strip() for line in quiz_text.strip().split('\n') if line.strip()]
        if len(lines) < 5:
            continue  # invalid

        question = lines[0]
        options = []
        correct_option_id = None

        for idx, option in enumerate(lines[1:]):
            if "✅" in option:
                correct_option_id = idx
                option = option.replace("✅", "").strip()
            options.append(option)

        if correct_option_id is None or len(options) < 2 or len(options) > 10:
            continue

        quizzes.append({
            "question": question,
            "options": options,
            "correct_option_id": correct_option_id,
            "explanation": explanation
        })

    if not quizzes:
        await update.message.reply_text("❌ Couldn’t parse any valid quiz. Make sure your format is correct.")
        return

    for quiz in quizzes:
        await context.bot.send_poll(
            chat_id=update.message.chat_id,
            question=quiz["question"],
            options=quiz["options"],
            type="quiz",
            correct_option_id=quiz["correct_option_id"],
            explanation=quiz["explanation"],
            is_anonymous=is_anonymous
        )

# Main function
def main():
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN environment variable not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_quiz_submission))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

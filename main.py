import re
import os
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Max limits by Telegram API
MAX_OPTION_LENGTH = 100
MAX_QUESTION_LENGTH = 300
MAX_EXPLANATION_LENGTH = 200

# Parses quiz blocks with ✅ marked correct answers
def parse_quiz_blocks(text):
    blocks = text.strip().split('\n\n')
    quizzes = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 6:
            continue

        question = lines[0].strip()[:MAX_QUESTION_LENGTH]
        options = []
        correct_option_id = -1

        for idx, line in enumerate(lines[1:5]):
            opt = line.replace("️", "").strip()
            if "✅" in opt:
                opt = opt.replace("✅", "").strip()
                correct_option_id = idx
            # Truncate to 100 characters
            options.append(opt[:MAX_OPTION_LENGTH])

        # Explanation
        explanation_line = next((line for line in lines if line.startswith("Ex:")), "Ex: No explanation")
        explanation_line = explanation_line.strip()[:MAX_EXPLANATION_LENGTH]

        # Validate parsed quiz
        if len(options) == 4 and correct_option_id != -1:
            quizzes.append({
                "question": question,
                "options": options,
                "correct_option_id": correct_option_id,
                "explanation": explanation_line
            })

    return quizzes

# Telegram handler
async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    quiz_list = parse_quiz_blocks(text)

    if not quiz_list:
        await update.message.reply_text("❌ Could not parse any valid quizzes.")
        return

    for quiz in quiz_list[:15]:  # Send up to 15 questions
        try:
            await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question=quiz["question"],
                options=quiz["options"],
                type=Poll.QUIZ,
                correct_option_id=quiz["correct_option_id"],
                explanation=quiz["explanation"],
                is_anonymous=False
            )
            await asyncio.sleep(2)  # Delay to avoid rate limiting
        except Exception as e:
            await update.message.reply_text(f"⚠️ Failed to send a quiz: {str(e)}")

# Entry point
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quiz_handler))
    print("✅ Bot is running...")
    app.run_polling()

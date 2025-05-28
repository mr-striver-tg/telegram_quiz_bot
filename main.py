import re
import os
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Parses quiz blocks with ✅ marked correct answers
def parse_quiz_blocks(text: str):
    questions = []
    blocks = text.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        question = lines[0].strip()
        options = []
        correct_option_id = -1
        explanation = ''
        for i, line in enumerate(lines[1:]):
            if line.startswith("Ex:"):
                explanation = line.strip()
                break
            option_text = line.replace("️", "").replace("✅", "").strip()
            options.append(option_text)
            if "✅" in line:
                correct_option_id = len(options) - 1
        if correct_option_id == -1 or len(options) < 2:
            continue
        questions.append({
            "question": question,
            "options": options,
            "correct_option_id": correct_option_id,
            "explanation": explanation
        })
    return questions

# Main handler for processing incoming messages
async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    quizzes = parse_quiz_blocks(text)

    if len(quizzes) < 1 or len(quizzes) > 15:
        await update.message.reply_text("❌ Please send between 1 and 15 quiz questions.")
        return

    for quiz in quizzes:
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=quiz["question"],
            options=quiz["options"],
            type=Poll.QUIZ,
            correct_option_id=quiz["correct_option_id"],
            explanation=quiz["explanation"],
            is_anonymous=False
        )
        await asyncio.sleep(1.5)

# Entry point
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quiz_handler))
    app.run_polling()

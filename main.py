import re
import os
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")  # Make sure this matches your .env variable

def parse_quiz_blocks(text):
    blocks = text.strip().split('\n\n')
    quizzes = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 6:
            continue

        question = lines[0]
        options = []
        correct_option_id = -1

        for idx, line in enumerate(lines[1:5]):
            opt = line.replace("️", "").strip()
            if "✅" in opt:
                opt = opt.replace("✅", "").strip()
                correct_option_id = idx
            options.append(opt)

        explanation_line = next((line for line in lines if line.startswith("Ex:")), "Ex: No explanation")

        quizzes.append({
            "question": question,
            "options": options,
            "correct_option_id": correct_option_id,
            "explanation": explanation_line
        })

    return quizzes


async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    quiz_list = parse_quiz_blocks(text)

    if not quiz_list:
        await update.message.reply_text("❌ Could not parse any quizzes.")
        return

    for quiz in quiz_list[:15]:  # limit to 15
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=quiz["question"],
            options=quiz["options"],
            type=Poll.QUIZ,
            correct_option_id=quiz["correct_option_id"],
            explanation=quiz["explanation"],
            is_anonymous=False
        )
        await asyncio.sleep(2)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), quiz_handler))
    app.run_polling()

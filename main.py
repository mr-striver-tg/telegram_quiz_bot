from telegram import Update, Poll
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os

TOKEN = os.getenv("8014250953:AAHQ2YZs3IJHPgZCY-ZsHH9CSrYRf30ZK_k")

def parse_quiz(text):
    lines = text.strip().split("\n")
    question = lines[0].strip()
    options = []
    correct_index = -1
    explanation = ""

    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Ex:"):
            explanation = line
            continue
        if "✅" in line:
            clean_line = line.replace("✅", "").strip()
            options.append(clean_line)
            correct_index = len(options) - 1
        else:
            options.append(line.strip())

    return question, options, correct_index, explanation

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    question, options, correct_index, explanation = parse_quiz(text)

    if correct_index == -1:
        await update.message.reply_text("❌ No correct answer found (✅ missing).")
        return

    await update.message.reply_poll(
        question=question,
        options=options,
        type=Poll.QUIZ,
        correct_option_id=correct_index,
        explanation=explanation,
        is_anonymous=False
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send your quiz with ✅ on the correct option!")

def main():
    app = Application.builder().token(8014250953:AAHQ2YZs3IJHPgZCY-ZsHH9CSrYRf30ZK_k).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

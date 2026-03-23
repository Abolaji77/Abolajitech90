import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your actual questions
QUIZ_DATA = [
    {"q": "What is SEO?", "a": "Search Engine Optimization"},
    {"q": "What does PPC stand for?", "a": "Pay Per Click"},
    {"q": "Which social platform is best for B2B?", "a": "LinkedIn"},
    {"q": "What is a CTA?", "a": "Call to Action"},
    {"q": "What is CTR?", "a": "Click Through Rate"}
]

# Simple in-memory storage (Resets on bot restart!)
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now()

    # Check if user is in "cool-down" period
    if user_id in user_progress and user_progress[user_id].get("next_available"):
        if now < user_progress[user_id]["next_available"]:
            await update.message.reply_text("You've finished this week's challenge! Come back next week.")
            return

    # Initialize user progress
    user_progress[user_id] = {"current_q": 0, "next_available": None}
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q_index = user_progress[user_id]["current_q"]

    if q_index < len(QUIZ_DATA):
        question = QUIZ_DATA[q_index]["q"]
        await update.message.reply_text(f"Question {q_index + 1}: {question}")
    else:
        # Quiz Finished
        user_progress[user_id]["next_available"] = datetime.now() + timedelta(days=7)
        await update.message.reply_text("Congratulations! You've completed 5 questions. Come back next week for new challenges!")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress or user_progress[user_id]["next_available"]:
        return

    # For simplicity, we just move to the next question regardless of answer
    user_progress[user_id]["current_q"] += 1
    await ask_question(update, context)

def main():
    # Use Environment Variable for security
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Render needs the bot to listen to a port or run as a background worker
    app.run_polling()

if __name__ == "__main__":
    main()

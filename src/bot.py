import asyncio
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.config import TELEGRAM_BOT_TOKEN
from src.rag_engine import rag_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def send_safe_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    """Send message attempting Markdown first, falling back to plain text if parsing fails."""
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning(f"Markdown parsing failed ({e}). Falling back to plain text format.")
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command in Telegram."""
    welcome_text = (
        "👋 **Welcome to TechUni Admissions Assistant!**\n\n"
        "I'm here to help you with any questions regarding:\n"
        "• 📚 Academic Programs & Levels\n"
        "• 💰 Tuition, Pricing & Scholarships\n"
        "• ⏰ Cohort Schedules & Remote/Hybrid Modalities\n"
        "• 📝 Admission Requirements & Registration\n"
        "• 🎓 Diplomas & Industry Certifications\n\n"
        "Feel free to ask your question below!"
    )
    if update.effective_chat:
        await send_safe_message(context, update.effective_chat.id, welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command in Telegram."""
    help_text = (
        "💡 **How can I help you?**\n\n"
        "You can ask me questions like:\n"
        "- *What is the price of the AI Engineering program?*\n"
        "- *Do you offer weekend or evening classes?*\n"
        "- *What are the requirements for admission?*\n"
        "- *Are there any early bird discounts?*\n\n"
        "If you ask something outside our admissions scope, I will connect you with a human advisor."
    )
    if update.effective_chat:
        await send_safe_message(context, update.effective_chat.id, help_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from Telegram users and query RAG engine asynchronously."""
    if not update.message or not update.message.text or not update.effective_chat:
        return

    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id

    logger.info(f"Received Telegram message from chat {chat_id}: '{user_text}'")

    # Send typing action to provide interactive feedback
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as e:
        logger.warning(f"Could not send typing action: {e}")

    # Process query asynchronously in a thread pool without blocking the Telegram event loop
    result = await asyncio.to_thread(rag_engine.query, user_text)
    answer = result.get("answer", "An error occurred while processing your request.")

    # Send answer safely back to Telegram user
    await send_safe_message(context, chat_id, answer)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler logging exceptions."""
    logger.error(f"Telegram handler error: {context.error}")


def create_bot_application():
    """Build and configure the Telegram application."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Telegram bot cannot be created.")
        return None

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    return application


def run_bot():
    """Run Telegram Bot in standalone polling mode."""
    app = create_bot_application()
    if app:
        logger.info("Starting Telegram Bot in polling mode...")
        app.run_polling()
    else:
        logger.error("Failed to run Telegram Bot. Check TELEGRAM_BOT_TOKEN in .env.")


if __name__ == "__main__":
    run_bot()

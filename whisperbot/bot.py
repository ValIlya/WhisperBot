import logging
import os
import traceback

from dotenv import load_dotenv
from telegram import File, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from whisperbot.chat import Chat, Role
from whisperbot.models import Message
from whisperbot.storage import Storage
from whisperbot.text_split import split

load_dotenv()


storage = Storage(
    connstring=os.getenv("MONGODB_CONN"),
    database=os.getenv("MONGO_DB"),
    collection=os.getenv("MONGO_COLLECTION"),
)

client = Chat(token=os.getenv("MISTAL_API_KEY"))
app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message = Message(sender=Role.USER, text=update.message.text)

    history = storage.get_messages(chat_id) + [message]
    storage.append_message(chat_id, message)

    reply = client.reply(messages=history)

    storage.append_message(chat_id, Message(sender=Role.ASSISTANT, text=reply))

    for text in split(reply):
        await update.message.reply_text(text)


async def get_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_file: File = await update.message.voice.get_file()
    await new_file.download_to_drive(f"{update.message.voice.file_id}.ogg")
    await update.message.reply_text("Voice note saved")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    storage.save_new_dialogue(chat_id)
    await update.message.reply_text("Welcome! Your chat history will be saved.")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Bot for chatting with LLM
 - /clearhistory to clear chat history and all llm context
""".strip()
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    storage.delete_chat_history(chat_id)
    await update.message.reply_text("Chat history cleared!")


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Starts the bot"),
            ("help", "Helps a lot"),
            ("clearhistory", "Clears chat history and all llm context"),
        ]
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)
    for text in split(tb_string):
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID or update.message.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )


def main():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("clearhistory", clear_history))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, get_voice))
    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

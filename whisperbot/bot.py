import io
import logging
import os
import traceback

import telegramify_markdown
from dotenv import load_dotenv
from telegram import File, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import Message as TMessage
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from whisperbot.chat import Chat, Role
from whisperbot.models import Message, UserData
from whisperbot.speech2text import Speech2Text
from whisperbot.storage import Storage
from whisperbot.text_split import split

load_dotenv()


storage = Storage(
    connstring=os.getenv("MONGODB_CONN"),
    database=os.getenv("MONGO_DB"),
    collection=os.getenv("MONGO_COLLECTION"),
)

client = Chat(token=os.getenv("MISTRAL_API_KEY"))
app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")
speech2text = Speech2Text(model=os.getenv("SPEECH2TEXT_MODEL"))


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def _answer(message: TMessage, context: ContextTypes.DEFAULT_TYPE):
    save_data = Message(sender=Role.USER, text=message.text)

    history = storage.get_messages(message.chat_id) + [save_data]
    storage.append_message(message.chat_id, save_data)

    reply = client.reply(messages=history)

    storage.append_message(message.chat_id, Message(sender=Role.ASSISTANT, text=reply))

    converted = telegramify_markdown.markdownify(reply)
    for text in split(converted):
        await message.reply_text(text=text, parse_mode="MarkdownV2")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _answer(message=update.message, context=context)


async def _transcribe(
    message: TMessage, context: ContextTypes.DEFAULT_TYPE, language: str | None = None
) -> None:
    new_file: File = await message.voice.get_file()
    stream = io.BytesIO(await new_file.download_as_bytearray())
    res = speech2text.transcribe(stream, language)
    text = res.text

    delete = InlineKeyboardButton("Delete", callback_data="delete")
    question = InlineKeyboardButton("Question", callback_data="question")
    lang_buttons = []
    lang_probs = [
        (lang, prob) for lang, prob in res.language_probs.items() if prob > 0.01
    ]
    lang_probs = sorted(lang_probs, key=lambda lang_prob: lang_prob[1], reverse=True)
    for lang, prob in lang_probs:
        lang_buttons.append(
            InlineKeyboardButton(f"Lang: {lang} ({prob*100:0.1f}%)", callback_data=lang)
        )

    reply_markup = InlineKeyboardMarkup([[delete, question], lang_buttons])

    await message.reply_text(text, reply_markup=reply_markup)


async def get_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    language = storage.get_language(update.message.chat_id)
    await _transcribe(message=update.message, context=context, language=language)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message = query.message
    if not isinstance(message, TMessage):
        return

    await query.edit_message_reply_markup(reply_markup=None)
    if query.data == "delete":
        return
    elif query.data == "question":
        await _answer(message=query.message, context=context)
    elif query.data in speech2text.get_available_languages():
        if message.reply_to_message:
            storage.set_language(message.chat_id, language=query.data)
            await _transcribe(
                message=message.reply_to_message, language=query.data, context=context
            )
        else:
            await message.reply_text("Audio message not found")


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


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if len(context.args) != 1:
        await update.message.reply_text("Set language with `/setlanguage en` command")
        return
    language = context.args[0]
    if language not in speech2text.get_available_languages():
        languages = ", ".join(speech2text.get_available_languages())
        await update.message.reply_text(
            f"Language {language} is not supported. Choose one from these: {languages}"
        )
        return
    storage.set_language(chat_id, language)
    await update.message.reply_text(f"Language is set to {language}!")


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Starts the bot"),
            ("help", "Helps a lot"),
            ("clearhistory", "Clears chat history and all llm context"),
            (
                "setlanguage",
                f"Sets language, '{UserData(chat_id=0).language}' by default",
            ),
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
    app.add_handler(CommandHandler("setlanguage", set_language))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, get_voice))
    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

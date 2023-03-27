import os
import logging
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import openai
import asyncio
import json
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

openai.api_key = os.environ["OPENAI_API_KEY"]
TG_USER_AUTH_TOKEN = os.environ["TELEGRAM_USER_TOKEN"]
CHAT_COMPLETION_MODEL = os.environ("CHAT_COMPLETION_MODEL", "gpt-3.5-turbo")
AUTHORIZED_USERS = []  # initialize the list of authorized users


def escape_markdown(text):
    escaped_chars = ["\\", ")"]
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    result = ""
    in_code_block = False

    for i, char in enumerate(text):
        # handle code blocks
        if text[i : i + 3] == "```":
            result += "```"
            in_code_block = not in_code_block
            i += 2
        elif in_code_block:
            result += char
        # escape any character with code between 1-126
        elif 1 <= ord(char) <= 126:
            result += "\\" + char
        # escape backslashes inside pre and code entities
        elif char == "\\" and ("`" in result or "`" in text[i + 1 : i + 4]):
            result += "\\\\"
        # escape parentheses inside inline link and custom emoji definition
        elif char in escaped_chars and "(" in result:
            result += "\\" + char
        # escape special characters in all other places
        elif char in special_chars:
            result += "\\" + char
        else:
            result += char

    return result


def authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.message.from_user.id
    if not sender_id in AUTHORIZED_USERS:
        return False
    return True


async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update=update, context=context):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Unauthorized"
        )
        return
    context.user_data["conversation_data"] = []
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Reset sucessfull"
    )


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Handle auth")
    sender_id = update.message.from_user.id
    if TG_USER_AUTH_TOKEN in update.message.text:
        logging.info("user added")
        AUTHORIZED_USERS.append(int(sender_id))
    if sender_id in AUTHORIZED_USERS:  # check if the sender is authorized
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"User {sender_id} has been authorized to use this bot.",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this command.",
        )


# Define a function to handle incoming messages
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update=update, context=context):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Unauthorized"
        )
        return

    message = update.message.text

    if "conversation_data" in context.user_data:
        logger.info("Loading 'conversation_data' from the chat.")
        conversation_history = context.user_data["conversation_data"]
        conversation_history.append({"role": "user", "content": message})
    else:
        conversation_history = [{"role": "user", "content": message}]
    logger.debug(f"Conversation_history {conversation_history}")

    chat_response = "Failed to get an answer."
    logging.info("Prepare response from OpenAI")
    try:
        response = openai.ChatCompletion.create(
            model=CHAT_COMPLETION_MODEL,
            messages=conversation_history,
        )
        logging.info(f"Received response from openai {response}")
        chat_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": chat_response})
        context.user_data["conversation_data"] = conversation_history

    except Exception as e:
        logging.error(e)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=escape_markdown(chat_response),
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )


async def start(update, context):
    if not authorized(update=update, context=context):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Unauthorized"
        )
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm a simple ChatGPT bot. Send me a message and I'll try to respond to it.",
    )


application = (
    ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).updater(None).build()
)
start_handler = CommandHandler("start", start)
auth_handler = CommandHandler("authorize", authorize)
reset_handler = CommandHandler("reset", reset_context)
message_handler = MessageHandler(filters.TEXT, process_message)

application.add_handler(auth_handler)
application.add_handler(reset_handler)
application.add_handler(start_handler)
application.add_handler(message_handler)


async def handle_update(event: Dict[str, Any]):
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    await application.update_queue.put()


async def run(event: Dict[str, Any]):
    async with application:
        logging.info(f"Process update")
        update = Update.de_json(data=event, bot=application.bot)
        await application.process_update(update)


# Define the Lambda handler function
def lambda_handler(event, context):
    logging.debug(f"received event {event}")
    event_body = json.loads(event["body"])
    try:
        asyncio.run(run(event_body))
    except Exception:
        application.bot.send_message(
            chat_id=event_body["message"]["chat"]["id"],
            text="Failed to process your request. Please reach support.",
        )
    return {"message": "Accepted", "status_code": 202}

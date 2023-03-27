import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import openai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize the OpenAI API by setting the `OPENAI_SECRET_KEY` environment variable and connecting to the API
openai.api_key = os.environ["OPENAI_API_KEY"]
TG_USER_AUTH_TOKEN = os.environ["TELEGRAM_USER_TOKEN"]
authorized_users = []  # initialize the list of authorized users


def authorize(update:Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.message.from_user.id
    if TG_USER_AUTH_TOKEN in update.message.text:
            authorized_users.append(int(sender_id))
    if sender_id in authorized_users:  # check if the sender is authorized
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"User {sender_id} has been authorized to use this bot.",
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this command.",
        )


# Define a function to handle incoming messages
async def chat(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    response = openai.Completion.create(
        engine="davinci",
        prompt=message,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response.choices[0].text
    )


# Define a function to handle the `/start` command
async def start(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm a simple ChatGPT bot. Send me a message and I'll try to respond to it.",
    )

application = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()
    
start_handler = CommandHandler('start', start)
auth_handler = CommandHandler('authorize', authorize)
application.add_handler(auth_handler)
application.add_handler(start_handler)



# Define the Lambda handler function
def lambda_handler(event, context):
    application.run_polling()
    return

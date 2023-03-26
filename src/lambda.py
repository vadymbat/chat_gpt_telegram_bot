import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai

# Initialize the OpenAI API by setting the `OPENAI_SECRET_KEY` environment variable and connecting to the API
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize the Telegram bot by creating an `Updater` object and passing in your bot token
bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
updater = Updater(token=os.environ["TELEGRAM_TOKEN"], use_context=True)
tg_user_auth_token = os.environ["TELEGRAM_USER_TOKEN"]
authorized_users = []  # initialize the list of authorized users


def authorize(update, context):
    sender_id = update.message.from_user.id
    if sender_id in authorized_users:  # check if the sender is authorized
        command, user_id = update.message.text.split()
        if command == "/authorize" and tg_user_auth_token in command:
            authorized_users.append(int(user_id))
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"User {user_id} has been authorized to use this bot.",
            )
        elif command == "/unauthorize":
            authorized_users.remove(int(user_id))
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"User {user_id} has been unauthorized from using this bot.",
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this command.",
        )


# Define a function to handle incoming messages
def chat(update, context):
    message = update.message.text
    response = openai.Completion.create(
        engine="davinci",
        prompt=message,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=response.choices[0].text
    )


# Define a function to handle the `/start` command
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm a simple ChatGPT bot. Send me a message and I'll try to respond to it.",
    )


# Add the command handler to the updater
start_handler = CommandHandler("start", start)
updater.dispatcher.add_handler(start_handler)

# Add the message handler to the updater
message_handler = MessageHandler(Filters.text & ~Filters.command, chat)
updater.dispatcher.add_handler(message_handler)
authorize_handler = CommandHandler(["authorize", "unauthorize"], authorize)
updater.dispatcher.add_handler(authorize_handler)


# Define the Lambda handler function
def lambda_handler(event, context):
    updater.start_polling()
    return

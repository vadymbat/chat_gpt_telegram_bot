# Telegram Chatbot with ChatGPT

## Introduction

Deploy your own Telegram chatbot that utilizes ChatGPT for conversational AI. The chatbot is built using Python and based on AWS Serverless architecture backed by AWS Lambda to process commands and Dynamo DB table to store registred users. All infrastructure is managed by Terraform.

## Requirements

To run this chatbot, you will need:
- OpenAI platform token from https://platform.openai.com/account/api-keys
- AWS Account
- Python 3.x
- Terraform
- Docker

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/vadymbat/chat_gpt_telegram_bot
   ```

2. Create a Telegram bot via [BotFather](https://core.telegram.org/bots#creating-a-new-bot). Register bot commands: `authorize` to login, `deauthorize` to logout and `reset` to remove bot message history. Save bot token for future steps.
```
authorize - login to use the bot
deauthorize - logout
reset - remove bot message history

```
3. Navigate to the terraform directory:

   ```
   cd infra
   ```

4. Initialize Terraform:

   ```
   terraform init
   ```

6. Apply Terraform, replace placeholders with your values, where `<telegram_user_auth_token>` some random password to activate the bot from telegram using command `/authorize <telegram_user_auth_token> `:

   ```
   terraform apply -var 'open_ai_token=<open_ai_token>' -var 'telegram_bot_token=<telegram_bot_token>' -var 'telegram_user_auth_token=<telegram_user_auth_token>'
   ```

7. Configure telegram webhook to your lambda url, which you get from terraform output `lambda_function_url`:
```
curl -X POST https://api.telegram.org/bot<telegram_bot_token>/setWebhook?url=<your_lambda_url>
```
8. Test the chatbot by sending a message to your Telegram bot!

## How to use
1. Run `/start`
2. Run `/authorize <telegram_user_auth_token>`
3. Start some conversation
4. Use `/reset` to remove message history when switching topic
5. You can share your bot with friends, by sharing a link and `<telegram_user_auth_token>`
6. Use `/deauthorize` to logout
## Limitation
- You need to send messages to keep container alive otherwise, the message history will be lost in about 3 minutes.

## Conclusion

Congratulations, you've successfully deployed a Telegram chatbot that utilizes ChatGPT on AWS Lambda with Terraform! Feel free to customize the chatbot's
variable "open_ai_token" {
  sensitive = true
}

variable "telegram_bot_token" {
  sensitive = true
}

variable "telegram_user_auth_token" {
  sensitive = true
}

variable "name_prefix" {
  default = "tg-chatgpt"
}

variable "lambda_log_level" {
  default = "INFO"
}

variable "chat_completion_model" {
  description = "ChatGPT model. List of available https://platform.openai.com/docs/models"
  default = "gpt-3.5-turbo"
}
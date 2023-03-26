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
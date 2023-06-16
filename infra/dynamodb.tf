resource "aws_dynamodb_table" "chat_gpt_tg_bot_users" {
  name           = "${var.name_prefix}-bot-users"
  hash_key       = "id" # telegram user id
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attribute {
    name = "id"
    type = "N"
  }
}

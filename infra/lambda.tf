module "lambda_chat_gpt" {
  source = "terraform-aws-modules/lambda/aws"

  create_function            = true # to control creation of the Lambda Function and related resources
  create_role                = true
  create_lambda_function_url = true

  function_name = "${var.name_prefix}-tg-message-handler"
  description   = "The lambda to handle tg messages"
  handler       = "app.lambda.lambda_handler"
  runtime       = "python3.9"
  publish       = true
  # reserved_concurrent_executions    = 0
  timeout                           = 300
  cloudwatch_logs_retention_in_days = 5

  layers = [
    module.layer.lambda_layer_arn
  ]
  environment_variables = {
    "LOG_LEVEL"             = var.lambda_log_level
    "OPENAI_API_KEY"        = var.open_ai_token
    "TELEGRAM_TOKEN"        = var.telegram_bot_token
    "TELEGRAM_USER_TOKEN"   = var.telegram_user_auth_token
    "CHAT_COMPLETION_MODEL" = var.chat_completion_model
    "USERS_DB_TABLE_NAME"   = aws_dynamodb_table.chat_gpt_tg_bot_users.name
  }
  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect = "Allow",
      actions = [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      resources = [aws_dynamodb_table.chat_gpt_tg_bot_users.arn]
    }
  }

  source_path = "${path.module}/../src"
  artifacts_dir = "${path.root}/builds/lambda_function_layer/"
}


module "layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_function = false
  create_layer    = true

  layer_name          = "${var.name_prefix}-tg-message-layer"
  compatible_runtimes = ["python3.9"]
  runtime             = "python3.9" # required to force layers to do pip install

  # build_in_docker = true
  # source_path = [
  #   "${path.module}/../src",
  #   {
  #     pip_requirements = "${path.module}/../src"
  #   }
  # ]

  build_in_docker = true
  docker_image    = "python:3.9-slim"
  docker_file     = "${path.module}/../src/Dockerfile"
  source_path = [{
    path             = "${path.module}/../src"
    pip_tmp_dir      = "${path.cwd}/../src"
    pip_requirements = "${path.module}/../src/requirements.txt"
    prefix_in_zip    = "python"
  }]
  artifacts_dir = "${path.root}/builds/lambda_function_layer/"
}

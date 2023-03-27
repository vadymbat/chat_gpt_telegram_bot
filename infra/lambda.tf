module "lambda_chat_gpt" {
  source = "terraform-aws-modules/lambda/aws"

  create_function = true # to control creation of the Lambda Function and related resources
  create_role     = true
  create_lambda_function_url = true

  function_name                     = "${var.name_prefix}-tg-message-handler"
  description                       = "The lambda to handle tg messages"
  handler                           = "lambda.lambda_handler"
  runtime                           = "python3.9"
  publish                           = true
  reserved_concurrent_executions    = 1
  cloudwatch_logs_retention_in_days = 5
  
  layers = [
    module.layer.lambda_layer_arn
  ]
  environment_variables = {
    "LOG_LEVEL"                    = "INFO"
    "OPENAI_API_KEY"               = var.open_ai_token
    "TELEGRAM_TOKEN"               = var.telegram_bot_token
    "TELEGRAM_USER_TOKEN"          = var.telegram_user_auth_token
  }

  source_path = "${path.module}/../src/lambda.py"
}


module "layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_function     = false
  create_layer        = true
  
  layer_name          = "${var.name_prefix}-tg-message-layer"
  compatible_runtimes = ["python3.9"]
  runtime = "python3.9" # required to force layers to do pip install
  
  build_in_docker = true
  source_path = [
    "${path.module}/../src",
    {
      pip_requirements = "${path.module}/../src"
    }
  ]
}

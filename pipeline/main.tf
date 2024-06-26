provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
  
}

# 1 Eventbridge Scheduler to target pipeline every minute
resource "aws_scheduler_schedule" "pipeline_scheduler" {
  name       = "poseidon-earthquake-pipeline-scheduler"
  description = "schedules the etl pipeline to run every minute"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(* * * * ? *)"

  target {
    arn      = aws_lambda_function.pipeline_lambda.arn
    role_arn = aws_iam_role.pipeline_scheduler_role.arn
    
  }
}


resource "aws_iam_role" "pipeline_scheduler_role" {
  name = "poseidon-pipeline-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }]
  })
}

resource "aws_iam_policy" "scheduler_execute_pipeline_policy" {
  name        = "poseidon-invoke-pipeline-lambda-policy"
  description = "Policy to allow scheduler to invoke etl pipeline lambda function"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = aws_lambda_function.pipeline_lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_pipeline_lambda_invoke_policy" {
  role       = aws_iam_role.pipeline_scheduler_role.name
  policy_arn = aws_iam_policy.scheduler_execute_pipeline_policy.arn
}

# --------------- END -----------------

# 2 Lambda function to run pipeline every minute

resource "aws_lambda_function" "pipeline_lambda" {
    function_name = "poseidon-earthquake-pipeline"
    role = aws_iam_role.pipeline_lambda_role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-poseidon-pipeline:latest" # TO FILL
    architectures = ["x86_64"]
    timeout = 45
    environment {
      variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        DB_USERNAME = var.DB_USERNAME
      }
    }
}

resource "aws_iam_role" "pipeline_lambda_role" {
  name = "poseidon-pipeline-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "pipeline_sns_policy" {
  name = "poseidon-pipeline-sns-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = "SNS:Publish",
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "pipeline_sns_policy_attachment" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.pipeline_sns_policy.arn
}

resource "aws_iam_policy" "pipeline_rds_access_policy" {
  name        = "poseidon-pipeline-rds-access-policy"
  description = "Policy to allow weekly reporting lambda to leverage database"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["rds:DescribeDBInstances", "rds:Connect","rds:DeleteRecords", "rds:ExecuteStatement"],
        Resource = "arn:aws:rds:eu-west-2:129033205317:db:c11-earthquake-monitoring-db"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_rds_access" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.pipeline_rds_access_policy.arn
}

# --------------- END ---------------------------
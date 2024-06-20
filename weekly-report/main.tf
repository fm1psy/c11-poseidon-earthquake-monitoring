provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
  
}

# 1 Eventbridge Scheduler to target report generator every friday at 9am
resource "aws_scheduler_schedule" "reporting_scheduler" {
  name       = "poseidon-earthquake-weekly-reporting-scheduler"
  description = "schedules the weekly PDF report generator to run daily at 9am"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = "" # TO FILL
    role_arn = "" # TO FILL
    
  }
}

resource "aws_iam_role" "reporting_scheduler_role" {
  name = "poseidon-weekly-reporting-scheduler-role"
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

resource "aws_iam_policy" "scheduler_execute_reporting_policy" {
  name        = "poseidon-invoke-weekly-reporting-lambda-policy"
  description = "Policy to allow scheduler to invoke weekly PDF reporting lambda function"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = "" # TO FILL
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_pipeline_lambda_invoke_policy" {
  role       = aws_iam_role.reporting_scheduler_role.name
  policy_arn = aws_iam_policy.scheduler_execute_reporting_policy.arn
}

#2 Lamdba Function that generates weekly report

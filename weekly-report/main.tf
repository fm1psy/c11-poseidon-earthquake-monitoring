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

  schedule_expression = "cron(55 23 ? * 1 *)"

  target {
    arn      = aws_lambda_function.reporting_lambda.arn
    role_arn = aws_iam_role.reporting_scheduler_role.arn
    
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
        Resource = aws_lambda_function.reporting_lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_reporting_lambda_invoke_policy" {
  role       = aws_iam_role.reporting_scheduler_role.name
  policy_arn = aws_iam_policy.scheduler_execute_reporting_policy.arn
}

#2 Lamdba Function that generates weekly report
# ------- Function ----------
resource "aws_lambda_function" "reporting_lambda" {
    function_name = "poseidon-weekly-reporting"
    role = aws_iam_role.reporting_lambda_role.arn
    package_type = "Image"
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-poseidon-reporting:latest" 
    architectures = ["x86_64"]
    memory_size = 5000
    timeout = 600
    environment {
      variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        DB_USERNAME = var.DB_USERNAME
        STORAGE_BUCKET_NAME = var.STORAGE_BUCKET_NAME
        SHAPEFILE_BUCKET_NAME = var.SHAPEFILE_BUCKET_NAME
      }
    }
}
# ------- END ----------

# ------- Permissions & Policies ----------
resource "aws_iam_role" "reporting_lambda_role" {
  name = "poseidon-weekly-reporting-lambda-role"
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

resource "aws_iam_policy" "reporting_s3_access_policy" {
  name        = "poseidon-reporting-s3-access-policy"
  description = "Policy to allow lambda to leverage s3 bucket"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject","s3:PutObject"],
        Resource = ["arn:aws:s3:::poseidon-weekly-reporting-storage/*", "arn:aws:s3:::poseidon-shapefiles/*"]
      },
      {
        Effect = "Allow",
        Action = ["s3:ListBucket"],
        Resource = ["arn:aws:s3:::poseidon-shapefiles"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "reporting_s3_access_attachmenet" {
  role       = aws_iam_role.reporting_lambda_role.name
  policy_arn = aws_iam_policy.reporting_s3_access_policy.arn
}

resource "aws_iam_policy" "reporting_rds_access_policy" {
  name        = "poseidon-reporting-rds-access-policy"
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
  role       = aws_iam_role.reporting_lambda_role.name
  policy_arn = aws_iam_policy.reporting_rds_access_policy.arn
}

# ------- END ----------
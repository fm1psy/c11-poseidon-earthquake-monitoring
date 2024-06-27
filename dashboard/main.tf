provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
  
}

# 1 Dashboard Task Definition
resource "aws_ecs_task_definition" "dashboard_task" {
  family                   = "poseidon-earthquake-dashboard-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 3072
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
  container_definitions = jsonencode([
    {
      name      = "poseidon-earthquake-dashboard-task"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-poseidon-dashboard:latest"
      essential = true
      environment = [
        {
            name = "DB_NAME",
            value = var.DB_NAME
        },
        {
            name = "DB_PORT"
            value = var.DB_PORT
        },
        {
            name = "DB_USERNAME"
            value = var.DB_USERNAME
        },
        {
            name = "DB_HOST"
            value = var.DB_HOST
        },
        {
            name = "DB_PASSWORD"
            value = var.DB_PASSWORD
        },
        {
          name = "BUCKET_NAME"
          value = var.BUCKET_NAME
        },
        {
          name = "SHAPEFILE_BUCKET_NAME"
          value = var.SHAPEFILE_BUCKET_NAME
        }

      ]
      portMappings = [
        {
            name = "earthquake-dash-80-tcp"
            containerPort = 80
            hostPort = 80
            protocol = "tcp"
            appProtocol = "http"
        },
        {
            name = "earthquake-dash-8501-tcp"
            containerPort = 8501
            hostPort = 8501
            protocol = "tcp"
        }
      ]
    }
  ])
}

# ------------- END -------------------------------
# 2 Dashboard Security Group
resource "aws_security_group" "dashboard_sg" {
  name        = "poseidon-dashboard-sg"
  vpc_id      = data.aws_vpc.c11_vpc.id
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 8501
    protocol    = "tcp"
    to_port     = 8501
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ------------- END --------------------------------

# 3 Dashboard Service
resource "aws_ecs_service" "dashboard_service" {
  name            = "earthquake-dashboard-service"
  cluster         = data.aws_ecs_cluster.c11_ecs_cluster.id
  task_definition = aws_ecs_task_definition.dashboard_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = ["subnet-0e6c6a8f959dae31a", "subnet-08781450402b81aa2", "subnet-07de213eeae1f6307"]
    security_groups = [aws_security_group.dashboard_sg.id]
    assign_public_ip = true
  }

}
# ------------- END --------------------------------




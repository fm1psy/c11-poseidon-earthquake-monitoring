provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
  
}

# 1 Security Group to allow RDS to listen to connections from Postgres default port
resource "aws_security_group" "db-security-group" {
    name = "c11-earthquake-monitoring-db-sg"
    vpc_id = data.aws_vpc.c11-vpc.id
    
    egress {
        from_port        = 0
        to_port          = 0
        protocol         = "-1"
        cidr_blocks      = ["0.0.0.0/0"]
    }

    ingress {
        from_port = var.DB_PORT
        to_port = var.DB_PORT
        protocol = "tcp"
        cidr_blocks      = ["0.0.0.0/0"]
    }
}

# 2 RDS to store real-time earthquake data
resource "aws_db_instance" "earthquake-monitoring-db" {
    allocated_storage            = 20
    db_name                      = var.DB_NAME
    identifier                   = "c11-earthquake-monitoring-db"
    engine                       = "postgres"
    engine_version               = "16.1"
    instance_class               = "db.t3.micro"
    publicly_accessible          = true
    performance_insights_enabled = false
    skip_final_snapshot          = true
    db_subnet_group_name         = "c11-public-subnet-group"
    vpc_security_group_ids       = [aws_security_group.db-security-group.id]
    username                     = var.DB_USERNAME
    password                     = var.DB_PASSWORD
}
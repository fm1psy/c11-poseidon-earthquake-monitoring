data "aws_ecs_cluster" "c11_ecs_cluster" {
  cluster_name = "c11-ecs-cluster"
}

data "aws_vpc" "c11_vpc" {
    id = "vpc-04b15cce2398e57f7"
}
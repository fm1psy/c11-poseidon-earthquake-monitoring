variable "AWS_ACCESS_KEY" {
    type = string
}

variable "AWS_SECRET_KEY" {
    type = string
}

variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable "DB_NAME" {
    type = string
}

variable "DB_USERNAME" {
    type = string
}

variable "DB_PASSWORD" {
  type = string
}

variable "DB_PORT" {
  type = number
  default = 5432
}

variable "DB_HOST" {
  type = string
}

variable "STORAGE_BUCKET_NAME" {
  type = string
}

variable "SHAPEFILE_BUCKET_NAME" {
  type = string
}
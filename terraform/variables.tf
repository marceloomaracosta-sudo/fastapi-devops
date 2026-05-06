variable "region" {
  default = "us-east-2"
}

variable "ami" {
  # Ubuntu 22.04 en us-east-2 (Ohio)
  default = "ami-07062e2a343acc423"
}

variable "key_name" {
  default = "devops-key"
}
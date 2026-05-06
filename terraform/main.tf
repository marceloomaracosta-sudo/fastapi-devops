# proveedor de AWS con la región definida en variables
provider "aws" {
  region = var.region
}

# security group que permite tráfico HTTP en puerto 8000 y SSH en puerto 22
resource "aws_security_group" "api_sg" {
  name = "api-sg"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# instancia EC2 donde va a correr la API
resource "aws_instance" "api_server" {
  ami                    = var.ami
  instance_type          = "t3.micro"  # capa gratuita de AWS
  vpc_security_group_ids = [aws_security_group.api_sg.id]
  key_name               = var.key_name

  # instala Docker y Docker Compose al iniciar la instancia
  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu
  EOF

  tags = {
    Name = "fastapi-devops"
  }
}
# muestra la IP pública de la instancia al terminar el apply
output "ip_publica" {
  value = aws_instance.api_server.public_ip
}
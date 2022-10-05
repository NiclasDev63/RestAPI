resource "aws_ecr_repository" "cloudbootcamp" {
  name                 = "cloudbootcamp_niclas_gregor_containerregistry"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
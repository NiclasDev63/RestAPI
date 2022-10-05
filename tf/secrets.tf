# Creating a AWS secret for database
resource "aws_secretsmanager_secret" "SQLCreds" {
   name = "DBcreds1"
}

# Creating a AWS secret versions for database
resource "aws_secretsmanager_secret_version" "sversion" {
  secret_id = aws_secretsmanager_secret.SQLCreds.id
  secret_string = jsonencode(yamldecode(data.aws_kms_secrets.creds.plaintext["db"]))
}

data "aws_kms_secrets" "creds" {
    secret{
        name="db"
        payload = file("${path.module}/db-creds.txt")
    }
}
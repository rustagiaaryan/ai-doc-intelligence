# S3 Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket for documents"
  value       = aws_s3_bucket.documents.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.documents.arn
}

output "s3_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.documents.region
}

output "s3_user_access_key_id" {
  description = "Access key ID for S3 user"
  value       = aws_iam_access_key.s3_user.id
  sensitive   = true
}

output "s3_user_secret_access_key" {
  description = "Secret access key for S3 user"
  value       = aws_iam_access_key.s3_user.secret
  sensitive   = true
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "RDS PostgreSQL address"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "Name of the database"
  value       = aws_db_instance.postgres.db_name
}

output "rds_connection_string" {
  description = "PostgreSQL connection string for asyncpg"
  value       = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${var.db_name}"
  sensitive   = true
}

# ElastiCache Outputs
output "elasticache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "elasticache_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}

output "elasticache_connection_string" {
  description = "Redis connection string"
  value       = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/0"
  sensitive   = true
}

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

# Kubernetes ConfigMap Values
output "kubernetes_configmap_values" {
  description = "Values to update in Kubernetes ConfigMap"
  value = {
    S3_BUCKET_NAME = aws_s3_bucket.documents.id
    S3_REGION      = aws_s3_bucket.documents.region
    S3_ENDPOINT_URL = ""
    REDIS_URL      = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/0"
    REDIS_URL_0    = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/0"
    REDIS_URL_1    = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/1"
    REDIS_URL_2    = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/2"
  }
}

# Kubernetes Secrets Values
output "kubernetes_secrets_values" {
  description = "Values to update in Kubernetes Secrets"
  value = {
    S3_ACCESS_KEY_ID     = aws_iam_access_key.s3_user.id
    S3_SECRET_ACCESS_KEY = aws_iam_access_key.s3_user.secret
    DATABASE_URL         = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${var.db_name}"
  }
  sensitive = true
}

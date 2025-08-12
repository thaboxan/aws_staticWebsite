# terraform/outputs.tf
output "website_url" {
  description = "Website URL (CloudFront)"
  value       = "https://${aws_cloudfront_distribution.website.domain_name}"
}

output "www_website_url" {
  description = "Alternative website URL"
  value       = "https://${aws_cloudfront_distribution.website.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID"
  value       = aws_cloudfront_distribution.website.id
}

output "cloudfront_domain_name" {
  description = "CloudFront Distribution Domain Name"
  value       = aws_cloudfront_distribution.website.domain_name
}

output "s3_bucket_name" {
  description = "S3 Bucket Name"
  value       = aws_s3_bucket.website.bucket
}

output "s3_bucket_website_endpoint" {
  description = "S3 Bucket Website Endpoint"
  value       = aws_s3_bucket_website_configuration.website.website_endpoint
}

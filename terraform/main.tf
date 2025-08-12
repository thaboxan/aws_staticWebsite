# terraform/main.tf

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# Random suffix for unique bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 bucket for static website hosting
resource "aws_s3_bucket" "website" {
  bucket = "${replace(var.domain_name, ".", "-")}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Static Website Bucket"
    Environment = var.environment
    Purpose     = "Portfolio Website"
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "website" {
  bucket = aws_s3_bucket.website.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket website configuration
resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# S3 bucket public access block (allow public access for website)
resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 bucket policy for public read access
resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id
  depends_on = [aws_s3_bucket_public_access_block.website]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.website.arn}/*"
      }
    ]
  })
}

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "website-oac"
  description                       = "Origin Access Control for Static Website"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "website" {
  origin {
    domain_name              = aws_s3_bucket.website.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.website.id
    origin_id                = "S3-${aws_s3_bucket.website.bucket}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Static website distribution for ${var.domain_name}"
  default_root_object = "index.html"

  # Remove aliases for now - can be added later when DNS is configured
  # aliases = [var.domain_name, "www.${var.domain_name}"]

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.website.bucket}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  custom_error_response {
    error_code         = 404
    response_code      = 404
    response_page_path = "/error.html"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 404
    response_page_path = "/error.html"
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "Static Website CloudFront"
    Environment = var.environment
    Purpose     = "Portfolio Website CDN"
  }
}

# Upload the main index.html file
resource "aws_s3_object" "index_html" {
  bucket       = aws_s3_bucket.website.id
  key          = "index.html"
  source       = "../dist/index_fixed.html"
  content_type = "text/html"
  etag         = filemd5("../dist/index_fixed.html")

  tags = {
    Name        = "Portfolio Index Page"
    Environment = var.environment
  }
}

# Upload all assets from the dist/assets folder
resource "aws_s3_object" "assets" {
  for_each = fileset("../dist/assets", "*")
  
  bucket = aws_s3_bucket.website.id
  key    = "assets/${each.value}"
  source = "../dist/assets/${each.value}"
  etag   = filemd5("../dist/assets/${each.value}")
  
  # Set content type based on file extension
  content_type = lookup({
    "css"  = "text/css"
    "js"   = "application/javascript"
    "png"  = "image/png"
    "jpg"  = "image/jpeg"
    "jpeg" = "image/jpeg"
    "gif"  = "image/gif"
    "svg"  = "image/svg+xml"
    "ico"  = "image/x-icon"
    "html" = "text/html"
    "json" = "application/json"
  }, split(".", each.value)[length(split(".", each.value)) - 1], "binary/octet-stream")

  tags = {
    Name        = "Portfolio Asset"
    Environment = var.environment
  }
}

# Create a simple error page
resource "aws_s3_object" "error_html" {
  bucket       = aws_s3_bucket.website.id
  key          = "error.html"
  content_type = "text/html"
  content = <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - Thabo Jafta</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
            text-align: center;
            background: #1a1a1a;
            color: #fff;
        }
        .error { 
            background: #2c3e50; 
            padding: 40px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        h1 { color: #317EFB; }
        a { 
            color: #317EFB; 
            text-decoration: none; 
            padding: 10px 20px;
            border: 2px solid #317EFB;
            border-radius: 5px;
            display: inline-block;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        a:hover { 
            background: #317EFB; 
            color: white; 
        }
    </style>
</head>
<body>
    <div class="error">
        <h1>404 - Page Not Found</h1>
        <p>Sorry, the page you're looking for doesn't exist.</p>
        <a href="/">Return to Portfolio</a>
    </div>
</body>
</html>
EOF

  tags = {
    Name        = "Error Page"
    Environment = var.environment
  }
}

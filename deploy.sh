echo "🚀 Deploying Thabo Jafta Portfolio Website..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &>/dev/null; then
    echo "❌ Terraform not installed. Please install Terraform first."
    exit 1
fi

# Navigate to terraform directory
cd terraform || exit 1

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate Terraform configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
read -p "Do you want to proceed with the deployment? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Applying Terraform configuration..."
    terraform apply tfplan
    
    echo "✅ Deployment completed!"
    echo "🌐 Your website will be available at:"
    terraform output website_url
    terraform output www_website_url
    
    echo "📝 CloudFront Distribution ID:"
    terraform output cloudfront_distribution_id
    
    echo "🪣 S3 Bucket:"
    terraform output s3_bucket_name
    
    echo "⏳ Note: DNS propagation and SSL certificate validation may take up to 20 minutes."
else
    echo "❌ Deployment cancelled."
    rm -f tfplan
fi
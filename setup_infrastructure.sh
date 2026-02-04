#!/bin/bash
# One-time infrastructure setup (run by infrastructure team)

set -e

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
ECR_REPO_NAME="${APPROVED_ECR_REPO:-bedrock-agents}"
S3_BUCKET_NAME="${SHARED_S3_BUCKET:-company-bedrock-agents}"

echo "=========================================="
echo "Infrastructure Setup for Bedrock Agents"
echo "=========================================="
echo "Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo ""

# 1. Create ECR Repository
echo "1. Creating ECR repository: $ECR_REPO_NAME"
aws ecr create-repository \
  --repository-name "$ECR_REPO_NAME" \
  --region "$AWS_REGION" \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256 \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || echo "   Repository already exists"

# Tag existing repository if it already exists
aws ecr tag-resource \
  --resource-arn "arn:aws:ecr:$AWS_REGION:$AWS_ACCOUNT_ID:repository/$ECR_REPO_NAME" \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || true

echo "   ✓ ECR repository ready"

# 2. Create S3 Bucket
echo ""
echo "2. Creating S3 bucket: $S3_BUCKET_NAME"
aws s3 mb "s3://$S3_BUCKET_NAME" --region "$AWS_REGION" 2>/dev/null || echo "   Bucket already exists"

# Add tags
aws s3api put-bucket-tagging \
  --bucket "$S3_BUCKET_NAME" \
  --tagging 'TagSet=[{Key=auto-delete,Value=no}]'

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket "$S3_BUCKET_NAME" \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket "$S3_BUCKET_NAME" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

echo "   ✓ S3 bucket ready"

# 3. Create Agent Execution Role
echo ""
echo "3. Creating IAM role: BedrockAgentExecutionRole"
aws iam create-role \
  --role-name BedrockAgentExecutionRole \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || echo "   Role already exists"

# Tag existing role if it already exists
aws iam tag-role \
  --role-name BedrockAgentExecutionRole \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || true

# Attach Bedrock policy
aws iam attach-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess \
  2>/dev/null || true

# Attach S3 access policy
cat > /tmp/s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$S3_BUCKET_NAME",
        "arn:aws:s3:::$S3_BUCKET_NAME/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3Access \
  --policy-document file:///tmp/s3-policy.json

echo "   ✓ IAM role ready"

# 4. Create Developer Policy
echo ""
echo "4. Creating IAM policy: BedrockAgentDeveloperPolicy"
aws iam create-policy \
  --policy-name BedrockAgentDeveloperPolicy \
  --policy-document file://iam-policy.json \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || echo "   Policy already exists"

# Tag existing policy if it already exists
aws iam tag-policy \
  --policy-arn "arn:aws:iam::$AWS_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy" \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || true

echo "   ✓ Developer policy ready"

# 5. Create folder structure in S3
echo ""
echo "5. Creating S3 folder structure"
aws s3api put-object --bucket "$S3_BUCKET_NAME" --key agents/ --content-length 0
aws s3api put-object --bucket "$S3_BUCKET_NAME" --key agents/sports-video-analyzer/ --content-length 0
aws s3api put-object --bucket "$S3_BUCKET_NAME" --key agents/sports-video-analyzer/videos/ --content-length 0
aws s3api put-object --bucket "$S3_BUCKET_NAME" --key agents/sports-video-analyzer/artifacts/ --content-length 0

echo "   ✓ S3 folders created"

echo ""
echo "=========================================="
echo "Infrastructure Setup Complete!"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  • ECR Repository: $ECR_REPO_NAME"
echo "  • S3 Bucket: $S3_BUCKET_NAME"
echo "  • IAM Role: BedrockAgentExecutionRole"
echo "  • IAM Policy: BedrockAgentDeveloperPolicy"
echo ""
echo "Next steps for developers:"
echo "  1. Attach BedrockAgentDeveloperPolicy to developer users/roles"
echo "  2. Run: python deploy_agent.py"
echo ""

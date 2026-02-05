#!/bin/bash
# One-time infrastructure setup (run by infrastructure team)

set -e

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-YOUR_ACCOUNT_ID}"
ECR_REPO_NAME="bedrock-agents"

echo "=========================================="
echo "Infrastructure Setup - New S3 + Existing ECR"
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

# 2. Create Agent Execution Role
echo ""
echo "2. Creating IAM role: BedrockAgentExecutionRole"
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

# Add S3 wildcard access policy (for any agent bucket)
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
        "arn:aws:s3:::*-data-$AWS_ACCOUNT_ID",
        "arn:aws:s3:::*-data-$AWS_ACCOUNT_ID/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3WildcardAccess \
  --policy-document file:///tmp/s3-policy.json

echo "   ✓ IAM role ready"

# 3. Create Developer Policy
echo ""
echo "3. Creating IAM policy: BedrockAgentPolicy"
aws iam create-policy \
  --policy-name BedrockAgentPolicy \
  --policy-document file://iam-policy.json \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || echo "   Policy already exists"

# Tag existing policy if it already exists
aws iam tag-policy \
  --policy-arn "arn:aws:iam::$AWS_ACCOUNT_ID:policy/BedrockAgentPolicy" \
  --tags Key=auto-delete,Value=no \
  2>/dev/null || true

echo "   ✓ Developer policy ready"

echo ""
echo "=========================================="
echo "Infrastructure Setup Complete!"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  • ECR Repository: $ECR_REPO_NAME"
echo "  • IAM Role: BedrockAgentExecutionRole"
echo "  • IAM Policy: BedrockAgentPolicy"
echo ""
echo "Note: S3 buckets will be created per agent"
echo ""
echo "Next steps for developers:"
echo "  1. Attach BedrockAgentPolicy to developer users/roles"
echo "  2. Run: python3 deploy_agent.py"
echo ""

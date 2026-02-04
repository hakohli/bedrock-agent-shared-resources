#!/bin/bash
# Tag existing resources with auto-delete: no

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="395102750341"
ECR_REPO_NAME="bedrock-agents"
S3_BUCKET_NAME="company-bedrock-agents"

echo "Tagging existing resources with auto-delete: no"
echo "================================================"

# Tag ECR repository
echo "1. Tagging ECR repository..."
aws ecr tag-resource \
  --resource-arn "arn:aws:ecr:$AWS_REGION:$AWS_ACCOUNT_ID:repository/$ECR_REPO_NAME" \
  --tags Key=auto-delete,Value=no \
  --region "$AWS_REGION" && echo "   ✓ ECR tagged"

# Tag S3 bucket
echo "2. Tagging S3 bucket..."
aws s3api put-bucket-tagging \
  --bucket "$S3_BUCKET_NAME" \
  --tagging 'TagSet=[{Key=auto-delete,Value=no}]' && echo "   ✓ S3 tagged"

# Tag IAM role
echo "3. Tagging IAM role..."
aws iam tag-role \
  --role-name BedrockAgentExecutionRole \
  --tags Key=auto-delete,Value=no && echo "   ✓ IAM role tagged"

# Tag IAM policy
echo "4. Tagging IAM policy..."
aws iam tag-policy \
  --policy-arn "arn:aws:iam::$AWS_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy" \
  --tags Key=auto-delete,Value=no && echo "   ✓ IAM policy tagged"

# Tag Bedrock agent
echo "5. Tagging Bedrock agent..."
if [ -f deployment_info.json ]; then
  AGENT_ID=$(python3 -c "import json; print(json.load(open('deployment_info.json'))['agent_id'])")
  aws bedrock-agent tag-resource \
    --resource-arn "arn:aws:bedrock:$AWS_REGION:$AWS_ACCOUNT_ID:agent/$AGENT_ID" \
    --tags auto-delete=no \
    --region "$AWS_REGION" && echo "   ✓ Bedrock agent tagged"
else
  echo "   ⊘ No agent deployed yet"
fi

echo ""
echo "✓ All resources tagged with auto-delete: no"

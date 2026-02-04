# Resource Tagging

All resources in this demo are tagged with `auto-delete: no` to prevent automatic cleanup.

## Tagged Resources

| Resource Type | Resource Name | Tag | Value |
|--------------|---------------|-----|-------|
| ECR Repository | bedrock-agents | auto-delete | no |
| S3 Bucket | company-bedrock-agents | auto-delete | no |
| IAM Role | BedrockAgentExecutionRole | auto-delete | no |
| IAM Policy | BedrockAgentDeveloperPolicy | auto-delete | no |
| Bedrock Agent | baseball-video-analyzer | auto-delete | no |

## Automatic Tagging

The `setup_infrastructure.sh` script automatically tags all resources during creation:

```bash
# ECR Repository
aws ecr create-repository \
  --repository-name bedrock-agents \
  --tags Key=auto-delete,Value=no

# S3 Bucket
aws s3api put-bucket-tagging \
  --bucket company-bedrock-agents \
  --tagging 'TagSet=[{Key=auto-delete,Value=no}]'

# IAM Role
aws iam create-role \
  --role-name BedrockAgentExecutionRole \
  --tags Key=auto-delete,Value=no

# IAM Policy
aws iam create-policy \
  --policy-name BedrockAgentDeveloperPolicy \
  --tags Key=auto-delete,Value=no

# Bedrock Agent (in deploy_agent.py)
bedrock.create_agent(
    agentName='baseball-video-analyzer',
    tags={'auto-delete': 'no'}
)
```

## Tag Existing Resources

If resources were created before tagging was implemented, use:

```bash
./tag_existing_resources.sh
```

## Verify Tags

Check tags on all resources:

```bash
# ECR
aws ecr list-tags-for-resource \
  --resource-arn arn:aws:ecr:us-east-1:395102750341:repository/bedrock-agents

# S3
aws s3api get-bucket-tagging --bucket company-bedrock-agents

# IAM Role
aws iam list-role-tags --role-name BedrockAgentExecutionRole

# IAM Policy
aws iam list-policy-tags \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy

# Bedrock Agent
aws bedrock-agent list-tags-for-resource \
  --resource-arn arn:aws:bedrock:us-east-1:395102750341:agent/R9ORLA8SGF
```

## Purpose

The `auto-delete: no` tag indicates these resources should be:
- ✅ Excluded from automated cleanup scripts
- ✅ Protected from accidental deletion
- ✅ Retained for production use
- ✅ Reviewed before any deletion

## Cost Tracking

Use this tag for cost allocation:

```bash
# AWS Cost Explorer filter
Tag: auto-delete = no
```

This helps track costs for persistent infrastructure vs. temporary resources.

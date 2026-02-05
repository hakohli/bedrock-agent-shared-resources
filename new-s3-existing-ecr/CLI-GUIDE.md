# CLI Migration Guide: New S3 + Existing ECR

**Deploy Bedrock agents with dedicated S3 buckets while sharing ECR repository**

---

## Overview

This guide shows how to deploy agents where each agent gets its own S3 bucket, but all agents share a common ECR repository.

**Time Required**: 10 minutes  
**Downtime**: None

---

## Prerequisites

✅ AWS CLI configured  
✅ Python 3.9+ installed  
✅ boto3 library installed

---

## Part 1: Infrastructure Setup (One-Time)

**Who**: Infrastructure team  
**When**: Once

### Step 1: Set Environment Variables

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
```

### Step 2: Run Infrastructure Setup

```bash
cd new-s3-existing-ecr
./setup_infrastructure.sh
```

**This creates**:
- ECR repository: `bedrock-agents` (shared)
- IAM role: `BedrockAgentExecutionRole`
- IAM policy: `BedrockAgentPolicy` (allows S3 bucket creation)

### Step 3: Attach Policy to Developers

```bash
# For individual user
aws iam attach-user-policy \
  --user-name developer-username \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentPolicy

# For developer group
aws iam attach-group-policy \
  --group-name developers \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentPolicy
```

---

## Part 2: Verify IAM Permissions (CRITICAL)

### Check Permissions

```bash
python3 verify_permissions.py
```

**Expected Results**:
- ✅ **PASS: BEDROCK** - Can create/update/delete agents
- ✅ **PASS: S3** - Can CREATE new S3 buckets
- ✅ **PASS: ECR** - Can push/pull from existing repository
- ✅ **PASS: IAM** - Can pass BedrockAgentExecutionRole
- ✅ **PASS: DENIED** - CANNOT create new ECR repositories

### What You SHOULD Have

```json
{
  "Allowed": [
    "bedrock:CreateAgent",
    "s3:CreateBucket",
    "s3:PutObject",
    "s3:GetObject",
    "ecr:PutImage",
    "ecr:BatchGetImage",
    "iam:PassRole"
  ]
}
```

### What You SHOULD NOT Have

```json
{
  "Denied": [
    "ecr:CreateRepository"
  ]
}
```

**Key Difference**: You CAN create S3 buckets (but with naming pattern `*-data-YOUR_ACCOUNT_ID`)

---

## Part 3: Deploy Agent with New S3 Bucket

### Step 1: Configure Agent

Edit `agent_config.py`:
```python
AGENT_CONFIG = {
    'agent_name': 'your-agent-name',  # Change this
    'description': 'Your agent description',
    'instruction': '''Your agent instructions''',
    'foundation_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'idle_session_ttl': 600
}
```

**S3 bucket will be auto-created**: `your-agent-name-data-YOUR_ACCOUNT_ID`

### Step 2: Deploy Agent

```bash
python3 deploy_agent.py
```

**What happens**:
1. Creates new S3 bucket: `{agent-name}-data-{account-id}`
2. Enables versioning and encryption on bucket
3. Tags bucket with `auto-delete: no`
4. Creates Bedrock agent
5. Prepares agent
6. Creates production alias
7. Saves deployment info

**Expected output**:
```
Creating S3 bucket: sports-video-analyzer-data-YOUR_ACCOUNT_ID
✓ S3 bucket created

Creating agent: sports-video-analyzer
✓ Agent created: ABCD1234

✓ Agent prepared
✓ Alias created: TSTALIASID

Deployment Complete!
```

### Step 3: Test Agent

```bash
python3 test_agent.py
```

---

## Part 4: Upload Videos

### Upload to Agent's Bucket

```bash
# Get bucket name from deployment
BUCKET_NAME=$(python3 -c "import json; print(json.load(open('deployment_info.json'))['s3_bucket'])")

# Upload video
aws s3 cp your-video.mp4 s3://$BUCKET_NAME/videos/your-video.mp4
```

---

## Part 5: Migrate Existing Agent

### Option A: Create New Agent with New Bucket

```bash
# Update agent_config.py with new agent name
python3 deploy_agent.py
```

### Option B: Update Existing Agent to Use New Bucket

```bash
# 1. Create new S3 bucket
AGENT_NAME="existing-agent"
BUCKET_NAME="$AGENT_NAME-data-YOUR_ACCOUNT_ID"

aws s3 mb s3://$BUCKET_NAME
aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
aws s3api put-bucket-tagging --bucket $BUCKET_NAME --tagging 'TagSet=[{Key=auto-delete,Value=no}]'

# 2. Copy data from old bucket
aws s3 sync s3://old-bucket/ s3://$BUCKET_NAME/

# 3. Update agent configuration to reference new bucket
# (Update in your application code)

# 4. Test with new bucket
# 5. Delete old bucket once verified
```

---

## Part 6: Cleanup

### Delete Agent and Its S3 Bucket

```bash
python3 cleanup.py
```

This will:
1. Delete the Bedrock agent
2. Empty the S3 bucket
3. Delete the S3 bucket

**Note**: Shared ECR repository is NOT deleted

---

## Key Differences from Shared S3 Approach

| Aspect | This Approach | Shared S3 Approach |
|--------|--------------|-------------------|
| **S3 Buckets** | New per agent | 1 shared bucket |
| **Bucket Naming** | `{agent}-data-{account}` | `company-bedrock-agents` |
| **Data Location** | `s3://agent-data-123/videos/` | `s3://shared/agents/agent/videos/` |
| **Can Create S3** | ✅ Yes (with pattern) | ❌ No |
| **Isolation** | Bucket-level | Prefix-level |
| **Cost** | Higher | Lower |

---

## Troubleshooting

### Issue: "Cannot create S3 bucket"

**Cause**: Bucket name doesn't match pattern `*-data-YOUR_ACCOUNT_ID`

**Solution**: Use the naming pattern in `agent_config.py`

### Issue: "Bucket already exists"

**Cause**: Bucket name is globally unique and taken

**Solution**: Change agent name or add suffix

### Issue: "Cannot create ECR repository"

**Expected**: This is correct! You should NOT be able to create ECR repositories

**Solution**: Use existing `bedrock-agents` repository

---

## Best Practices

1. **Naming Convention**: Use pattern `{agent-name}-data-{account-id}`
2. **Tagging**: Always tag buckets with `auto-delete: no`
3. **Encryption**: Enable encryption on all buckets
4. **Versioning**: Enable versioning for data protection
5. **Lifecycle Policies**: Set up lifecycle rules for cost optimization
6. **Monitoring**: Enable S3 access logging

---

## Cost Optimization

### Per-Bucket Costs

- S3 bucket: No charge for bucket itself
- Storage: $0.023/GB/month (Standard)
- Requests: $0.0004/1000 PUT, $0.0004/1000 GET

### Reduce Costs

```bash
# Set up lifecycle policy to move old data to cheaper storage
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-bucket-name \
  --lifecycle-configuration file://lifecycle-policy.json
```

Example `lifecycle-policy.json`:
```json
{
  "Rules": [{
    "Id": "MoveToIA",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 30,
      "StorageClass": "STANDARD_IA"
    }]
  }]
}
```

---

## Summary

**What You Get**:
- ✅ Dedicated S3 bucket per agent
- ✅ Shared ECR repository
- ✅ Bucket-level data isolation
- ✅ Self-service deployment

**What You Cannot Do**:
- ❌ Create new ECR repositories
- ❌ Create S3 buckets outside naming pattern

**Next Steps**:
1. Deploy multiple agents
2. Each gets its own S3 bucket
3. All share the same ECR repository

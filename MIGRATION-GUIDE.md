# Migration Guide: Use Existing ECR & S3 with Bedrock Agents

**Quick reference for converting existing agents to use shared infrastructure**

---

## Overview

Convert your Bedrock agent deployment to use existing ECR repository and S3 bucket instead of creating new ones.

**Time Required**: 10 minutes  
**Downtime**: None (deploy new, test, then remove old)

---

## Prerequisites

✅ Existing ECR repository: `bedrock-agents`  
✅ Existing S3 bucket: `company-bedrock-agents`  
✅ IAM role: `BedrockAgentExecutionRole`  
✅ IAM policy: `BedrockAgentDeveloperPolicy` attached to your user/role

---

## Changes Required

### 1. Update Agent Configuration

**Before** (creates new resources):
```python
agent = bedrock.create_agent(
    agentName='my-agent',
    # Uses default resource creation
)
```

**After** (uses existing resources):
```python
# Set environment variables
AWS_ACCOUNT_ID = 'YOUR_ACCOUNT_ID'
AWS_REGION = 'us-east-1'
SHARED_S3_BUCKET = 'company-bedrock-agents'
AGENT_EXECUTION_ROLE = f'arn:aws:iam::{AWS_ACCOUNT_ID}:role/BedrockAgentExecutionRole'

# Create agent with existing role
agent = bedrock.create_agent(
    agentName='my-agent',
    agentResourceRoleArn=AGENT_EXECUTION_ROLE,  # Use existing role
    foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
    instruction='Your agent instructions',
    tags={'auto-delete': 'no'}
)
```

### 2. Update S3 References

**Before**:
```python
# Agent creates its own bucket
s3_uri = 's3://my-agent-bucket-12345/data/'
```

**After**:
```python
# Use shared bucket with agent-specific prefix
agent_name = 'my-agent'
s3_uri = f's3://{SHARED_S3_BUCKET}/agents/{agent_name}/data/'
```

### 3. Update ECR References (if using containers)

**Before**:
```python
ecr_repo = 'my-agent-repo'
image_uri = f'{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ecr_repo}:latest'
```

**After**:
```python
ecr_repo = 'bedrock-agents'  # Shared repository
image_uri = f'{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ecr_repo}:{agent_name}'
```

### 4. Update IAM Permissions

**Remove** these permissions from your deployment scripts:
```json
{
  "Action": [
    "ecr:CreateRepository",
    "s3:CreateBucket"
  ]
}
```

**Verify** you have these permissions:
```json
{
  "Action": [
    "bedrock:CreateAgent",
    "bedrock:UpdateAgent",
    "ecr:PutImage",
    "ecr:BatchGetImage",
    "s3:PutObject",
    "s3:GetObject",
    "iam:PassRole"
  ]
}
```

---

## Step-by-Step Migration

### Step 1: Verify Access
```bash
python3 verify_permissions.py
```
Expected: All checks pass ✓

### Step 2: Update Your Deployment Script

Replace your agent creation code with:
```python
import boto3

bedrock = boto3.client('bedrock-agent', region_name='us-east-1')

response = bedrock.create_agent(
    agentName='your-agent-name',
    agentResourceRoleArn='arn:aws:iam::YOUR_ACCOUNT_ID:role/BedrockAgentExecutionRole',
    description='Your agent description',
    foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
    instruction='Your agent instructions',
    idleSessionTTLInSeconds=600,
    tags={'auto-delete': 'no'}
)

agent_id = response['agent']['agentId']
```

### Step 3: Update S3 Paths

Replace all S3 references:
```python
# Old
s3_path = 's3://old-bucket/file.txt'

# New
s3_path = f's3://company-bedrock-agents/agents/{agent_name}/file.txt'
```

### Step 4: Deploy New Agent
```bash
python3 deploy_agent.py
```

### Step 5: Test New Agent
```bash
python3 test_agent.py
```

### Step 6: Clean Up Old Resources (Optional)

After verifying the new agent works:
```bash
# Delete old agent
aws bedrock-agent delete-agent --agent-id OLD_AGENT_ID

# Delete old S3 bucket (if safe)
aws s3 rb s3://old-agent-bucket --force

# Delete old ECR repository (if safe)
aws ecr delete-repository --repository-name old-agent-repo --force
```

---

## Configuration File Template

Create `agent_config.py`:
```python
import os

# AWS Configuration
AWS_REGION = 'us-east-1'
AWS_ACCOUNT_ID = 'YOUR_ACCOUNT_ID'

# Shared Resources
APPROVED_ECR_REPO = 'bedrock-agents'
SHARED_S3_BUCKET = 'company-bedrock-agents'
AGENT_EXECUTION_ROLE = f'arn:aws:iam::{AWS_ACCOUNT_ID}:role/BedrockAgentExecutionRole'

# Your Agent Configuration
AGENT_CONFIG = {
    'agent_name': 'your-agent-name',
    'description': 'Your agent description',
    'instruction': 'Your agent instructions',
    'foundation_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'idle_session_ttl': 600
}

# S3 Paths
S3_AGENT_PREFIX = f's3://{SHARED_S3_BUCKET}/agents/{AGENT_CONFIG["agent_name"]}'
S3_DATA_PATH = f'{S3_AGENT_PREFIX}/data/'
S3_ARTIFACTS_PATH = f'{S3_AGENT_PREFIX}/artifacts/'
```

---

## Common Issues & Solutions

### Issue: "AccessDenied" when creating agent
**Solution**: Ensure `BedrockAgentDeveloperPolicy` is attached to your user/role
```bash
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

### Issue: "Role cannot be assumed"
**Solution**: Verify the execution role exists and has correct trust policy
```bash
aws iam get-role --role-name BedrockAgentExecutionRole
```

### Issue: "Bucket does not exist"
**Solution**: Verify shared bucket exists
```bash
aws s3 ls s3://company-bedrock-agents/
```

### Issue: Can still create buckets/repos
**Solution**: You have admin access. In production, the deny policy will block this.

---

## Verification Checklist

- [ ] Agent uses `BedrockAgentExecutionRole` (not creating new role)
- [ ] S3 paths use `company-bedrock-agents` bucket
- [ ] ECR images use `bedrock-agents` repository
- [ ] Agent tagged with `auto-delete: no`
- [ ] No new ECR repositories created
- [ ] No new S3 buckets created
- [ ] Agent deploys successfully
- [ ] Agent responds to test queries

---

## Quick Reference

| What | Old Approach | New Approach |
|------|-------------|--------------|
| **ECR** | Create per agent | Use `bedrock-agents` |
| **S3** | Create per agent | Use `company-bedrock-agents/agents/{name}/` |
| **IAM Role** | Create per agent | Use `BedrockAgentExecutionRole` |
| **Deployment** | Requires admin | Self-service with restricted policy |
| **Cost** | High (duplicate resources) | Low (shared infrastructure) |

---

## Support

- **Demo files**: `/Users/hakohli/bedrock-agent-demo/`
- **Full README**: `README.md`
- **Tagging guide**: `TAGGING.md`
- **Test script**: `python3 verify_permissions.py`

---

## Summary

**3 Key Changes**:
1. Use `BedrockAgentExecutionRole` instead of creating new IAM role
2. Use `company-bedrock-agents/agents/{agent-name}/` instead of new S3 bucket
3. Use `bedrock-agents` ECR repo with agent-specific tags

**Result**: Self-service deployment with shared infrastructure ✅

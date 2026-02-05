# Console Migration Guide: New S3 + Existing ECR

**Deploy Bedrock agents with dedicated S3 buckets via AWS Console**

---

## Overview

Deploy agents where each agent gets its own S3 bucket, but all share a common ECR repository.

**Time Required**: 15 minutes  
**Downtime**: None

---

## Part 1: Infrastructure Setup (One-Time)

### Step 1: Create ECR Repository

1. Go to **ECR Console**: https://console.aws.amazon.com/ecr/
2. Click **Create repository**
3. Configure:
   - **Repository name**: `bedrock-agents`
   - **Scan on push**: Enabled
   - **Encryption**: AES-256
4. **Add tag**: `auto-delete` = `no`
5. Click **Create repository**

### Step 2: Create IAM Execution Role

1. Go to **IAM Console**: https://console.aws.amazon.com/iam/
2. Click **Roles** → **Create role**
3. **Trusted entity**: AWS service → Bedrock
4. **Permissions**: `AmazonBedrockFullAccess`
5. **Role name**: `BedrockAgentExecutionRole`
6. Click **Create role**
7. Click on the role → **Add permissions** → **Create inline policy**
8. **JSON**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::*-data-YOUR_ACCOUNT_ID",
      "arn:aws:s3:::*-data-YOUR_ACCOUNT_ID/*"
    ]
  }]
}
```
9. **Policy name**: `S3WildcardAccess`
10. Click **Create policy**

### Step 3: Create IAM Developer Policy

1. **IAM Console** → **Policies** → **Create policy**
2. **JSON**: Paste content from `iam-policy.json`
3. **Policy name**: `BedrockAgentPolicy`
4. **Add tag**: `auto-delete` = `no`
5. Click **Create policy**

### Step 4: Attach Policy to Users

1. **IAM Console** → **Users** → Select user
2. **Add permissions** → **Attach policies**
3. Select `BedrockAgentPolicy`
4. Click **Add permissions**

---

## Part 2: Verify IAM Permissions (CRITICAL)

### Test 1: Create S3 Bucket (Should SUCCEED)

1. Go to **S3 Console**
2. Click **Create bucket**
3. **Bucket name**: `test-agent-data-YOUR_ACCOUNT_ID`
4. Click **Create bucket**
5. **Expected**: ✅ Bucket created successfully
6. Delete the test bucket

### Test 2: Create ECR Repository (Should FAIL)

1. Go to **ECR Console**
2. Click **Create repository**
3. **Repository name**: `test-should-fail`
4. Click **Create repository**
5. **Expected**: ❌ Access Denied error

### Test 3: Access Existing ECR (Should SUCCEED)

1. Go to **ECR Console**
2. Click on `bedrock-agents` repository
3. **Expected**: ✅ Can view repository

---

## Part 3: Create Agent with New S3 Bucket

### Step 1: Create S3 Bucket for Agent

1. Go to **S3 Console**: https://console.aws.amazon.com/s3/
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `sports-video-analyzer-data-YOUR_ACCOUNT_ID`
   - **Region**: us-east-1
   - **Block public access**: Enabled
   - **Versioning**: Enabled
   - **Encryption**: SSE-S3
4. **Add tag**: `auto-delete` = `no`
5. Click **Create bucket**
6. Create folders:
   - `videos/`
   - `artifacts/`

### Step 2: Create Bedrock Agent

1. Go to **Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. Click **Agents** → **Create Agent**
3. **Agent name**: `sports-video-analyzer`
4. **Description**: `Analyzes sports videos`
5. **Instructions**:
```
You are a sports video analysis assistant. You help users analyze sports game footage to extract:
- Scoreboard information (teams, scores, time/period, game state)
- Player identification (jersey numbers, positions, names)
- Key plays (goals, assists, shots, passes, defensive actions, scoring plays)
You can analyze videos from various sports.
```
6. **Model**: Anthropic Claude 3 Sonnet
7. **Service role**: `BedrockAgentExecutionRole`
8. Click **Create Agent**

### Step 3: Prepare and Create Alias

1. Click **Prepare** button
2. Wait for preparation (~30 seconds)
3. Click **Aliases** tab → **Create alias**
4. **Alias name**: `production`
5. Click **Create alias**

### Step 4: Add Tags

1. Click **Tags** tab → **Manage tags**
2. **Add tag**: `auto-delete` = `no`
3. Click **Save**

---

## Part 4: Upload Videos

### Upload via Console

1. Go to **S3 Console**
2. Navigate to: `sports-video-analyzer-data-YOUR_ACCOUNT_ID`
3. Click into `videos/` folder
4. Click **Upload** → **Add files**
5. Select your video files
6. Click **Upload**

---

## Part 5: Test Agent

### Test in Console

1. Go to **Bedrock Console** → **Agents**
2. Click on your agent
3. Click **Test** button
4. Enter prompt:
```
Analyze this video: s3://sports-video-analyzer-data-YOUR_ACCOUNT_ID/videos/your-video.mp4
```
5. Review response

---

## Part 6: Migrate Existing Agent

### Option A: Create New Agent

Follow Part 3 steps with a different agent name and bucket

### Option B: Update Existing Agent

1. Create new S3 bucket (Part 3, Step 1)
2. Copy data from old bucket:
   - Use S3 Console → Select files → **Copy**
   - Paste into new bucket
3. Update agent to reference new bucket
4. Test thoroughly
5. Delete old bucket

---

## Part 7: Cleanup

### Delete Agent and Bucket

1. **Delete Agent**:
   - Bedrock Console → Agents → Select agent
   - **Actions** → **Delete**
   
2. **Empty S3 Bucket**:
   - S3 Console → Select bucket
   - **Empty** → Confirm
   
3. **Delete S3 Bucket**:
   - Select bucket → **Delete** → Confirm

---

## Verification Checklist

- [ ] **IAM Permissions Verified**
  - Can CREATE S3 buckets with pattern `*-data-YOUR_ACCOUNT_ID`
  - CANNOT create ECR repositories
  - Can access existing ECR repository

- [ ] **ECR Repository exists**
  - Repository: `bedrock-agents`
  
- [ ] **S3 Bucket created per agent**
  - Bucket name: `{agent-name}-data-{account-id}`
  - Versioning enabled
  - Encryption enabled
  - Tagged: `auto-delete: no`
  
- [ ] **Agent created**
  - Uses `BedrockAgentExecutionRole`
  - Status: Prepared
  - Alias: production
  - Tagged: `auto-delete: no`

---

## Key Differences from Shared S3

| Aspect | New S3 Per Agent | Shared S3 |
|--------|-----------------|-----------|
| **S3 Buckets** | One per agent | One shared |
| **Can Create S3** | ✅ Yes | ❌ No |
| **Bucket Name** | `agent-data-123` | `company-bedrock-agents` |
| **Data Path** | `s3://agent-data-123/videos/` | `s3://shared/agents/agent/videos/` |
| **Isolation** | Bucket-level | Prefix-level |

---

## Troubleshooting

### Issue: Cannot create S3 bucket

**Check**: Bucket name must match pattern `*-data-YOUR_ACCOUNT_ID`

**Solution**: Use correct naming pattern

### Issue: Bucket name already taken

**Cause**: S3 bucket names are globally unique

**Solution**: Add suffix or change agent name

### Issue: Agent cannot access bucket

**Check**: 
1. IAM Console → Roles → `BedrockAgentExecutionRole`
2. Verify S3WildcardAccess policy exists

**Solution**: Add S3 permissions to role

---

## Best Practices

1. **Naming**: Use `{agent-name}-data-{account-id}` pattern
2. **Tagging**: Tag all resources with `auto-delete: no`
3. **Encryption**: Always enable encryption
4. **Versioning**: Enable for data protection
5. **Lifecycle**: Set up lifecycle policies for cost savings
6. **Monitoring**: Enable S3 access logging

---

## Console URLs

| Service | URL |
|---------|-----|
| Bedrock Agents | https://console.aws.amazon.com/bedrock/home#/agents |
| S3 Buckets | https://console.aws.amazon.com/s3/ |
| ECR Repositories | https://console.aws.amazon.com/ecr/ |
| IAM Roles | https://console.aws.amazon.com/iam/home#/roles |
| IAM Policies | https://console.aws.amazon.com/iam/home#/policies |

---

## Summary

**What You Get**:
- ✅ Dedicated S3 bucket per agent
- ✅ Shared ECR repository
- ✅ Bucket-level isolation
- ✅ Self-service deployment

**What You Cannot Do**:
- ❌ Create ECR repositories
- ❌ Create S3 buckets outside naming pattern

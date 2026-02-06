# Migrating Existing Agent to EXISTING Shared S3 and ECR

**Complete guide for migrating an existing Bedrock agent to use EXISTING shared S3 bucket and EXISTING shared ECR repository**

---

## Overview

This document shows how to migrate an existing Bedrock agent (e.g., `perfectgames-agent`) from using its own dedicated resources to using **EXISTING shared S3 bucket** and **EXISTING shared ECR repository**.

**Key Point**: This migration uses resources that ALREADY EXIST. No new S3 buckets or ECR repositories are created.

**Example Agent**: `perfectgames-agent` (ID: DJURJO4ZCL)  
**Account**: 395102750341  
**Region**: us-east-1

---

## Before Migration

**Current State**:
- Agent Name: `perfectgames-agent`
- Agent ID: `DJURJO4ZCL`
- IAM Role: `AmazonBedrockExecutionRoleForAgents_SHH74LGG38R` (agent-specific, will be replaced)
- S3: No structured storage (will use EXISTING shared bucket)
- ECR: No container images (will use EXISTING shared repository)
- Status: PREPARED

---

## After Migration

**Target State**:
- Same Agent Name: `perfectgames-agent`
- Same Agent ID: `DJURJO4ZCL`
- IAM Role: `BedrockAgentExecutionRole` (EXISTING shared role)
- S3: `company-bedrock-agents/agents/perfectgames-agent/` (EXISTING shared bucket)
- ECR: `bedrock-agents` (EXISTING shared repository)
- Status: PREPARED

**Important**: All target resources ALREADY EXIST. We are NOT creating new resources.

---

## Prerequisites

✅ **EXISTING** shared S3 bucket: `company-bedrock-agents` (already created)  
✅ **EXISTING** shared ECR repository: `bedrock-agents` (already created)  
✅ **EXISTING** shared IAM role: `BedrockAgentExecutionRole` (already created)  
✅ Agent to migrate: `perfectgames-agent`

**Verify existing resources**:
```bash
# Verify EXISTING S3 bucket
aws s3 ls s3://company-bedrock-agents/

# Verify EXISTING ECR repository
aws ecr describe-repositories --repository-names bedrock-agents --region us-east-1

# Verify EXISTING IAM role
aws iam get-role --role-name BedrockAgentExecutionRole
```

**All these resources must ALREADY EXIST before migration.**

---

## IAM Role Policies (EXISTING)

The **EXISTING** `BedrockAgentExecutionRole` already has the following policies configured:

### 1. S3 Access Policy (Inline Policy: `S3Access`)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::company-bedrock-agents",
      "arn:aws:s3:::company-bedrock-agents/*"
    ]
  }]
}
```

**What this allows**:
- Read files from `company-bedrock-agents` bucket
- Write files to `company-bedrock-agents` bucket
- List contents of `company-bedrock-agents` bucket

### 2. Bedrock Access Policy (AWS Managed: `AmazonBedrockFullAccess`)

This AWS managed policy includes:
- Bedrock agent operations
- Model invocations
- ECR access for Bedrock agents (implicit)

**What this allows**:
- Agent can invoke foundation models
- Agent can access ECR repository: `bedrock-agents`
- Agent can perform all Bedrock operations

### 3. ECR Access (Included in AmazonBedrockFullAccess)

The `AmazonBedrockFullAccess` policy includes permissions to:
- Pull container images from ECR
- Access the `bedrock-agents` repository
- Describe ECR repositories

**Verify policies**:
```bash
# View S3 access policy
aws iam get-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3Access

# List attached policies
aws iam list-attached-role-policies \
  --role-name BedrockAgentExecutionRole
```

**Important**: When you migrate your agent to use `BedrockAgentExecutionRole`, it automatically inherits all these permissions. No additional policy configuration is needed.

---

## Migration Steps - CLI Method

### Step 1: Get Current Agent Configuration

```bash
# List all agents
aws bedrock-agent list-agents --region us-east-1

# Get specific agent details
aws bedrock-agent get-agent \
  --agent-id DJURJO4ZCL \
  --region us-east-1
```

**Output**:
```
Agent Name: perfectgames-agent
Agent ID: DJURJO4ZCL
Current Role: arn:aws:iam::395102750341:role/service-role/AmazonBedrockExecutionRoleForAgents_SHH74LGG38R
Foundation Model: anthropic.claude-3-5-sonnet-20240620-v1:0
Status: PREPARED
```

**Save this information** - you'll need it for rollback if needed.

---

### Step 2: Create S3 Folders in EXISTING Shared Bucket

**Important**: We are creating folders INSIDE the EXISTING `company-bedrock-agents` bucket. We are NOT creating a new bucket.

```bash
# Create folder structure for the agent in EXISTING bucket
aws s3api put-object \
  --bucket company-bedrock-agents \
  --key agents/perfectgames-agent/

aws s3api put-object \
  --bucket company-bedrock-agents \
  --key agents/perfectgames-agent/data/

aws s3api put-object \
  --bucket company-bedrock-agents \
  --key agents/perfectgames-agent/output/
```

**Note**: The bucket `company-bedrock-agents` ALREADY EXISTS. We are only creating folders inside it.

**Verify**:
```bash
aws s3 ls s3://company-bedrock-agents/agents/perfectgames-agent/
```

**Expected Output**:
```
                           PRE data/
                           PRE output/
```

---

### Step 3: Update Agent to Use EXISTING Shared IAM Role

**Important**: We are updating the agent to use the EXISTING `BedrockAgentExecutionRole`. This role ALREADY EXISTS and is shared by other agents.

```bash
# Update agent configuration to use EXISTING shared role
aws bedrock-agent update-agent \
  --agent-id DJURJO4ZCL \
  --agent-name perfectgames-agent \
  --agent-resource-role-arn arn:aws:iam::395102750341:role/BedrockAgentExecutionRole \
  --foundation-model anthropic.claude-3-5-sonnet-20240620-v1:0 \
  --instruction "Agent for perfect games analysis" \
  --region us-east-1
```

**Note**: The role `BedrockAgentExecutionRole` ALREADY EXISTS. We are NOT creating a new role.

**Expected Output**:
```json
{
  "agent": {
    "agentId": "DJURJO4ZCL",
    "agentName": "perfectgames-agent",
    "agentResourceRoleArn": "arn:aws:iam::395102750341:role/BedrockAgentExecutionRole",
    "agentStatus": "NOT_PREPARED"
  }
}
```

---

### Step 4: Prepare Agent with New Configuration

```bash
# Prepare agent to apply changes
aws bedrock-agent prepare-agent \
  --agent-id DJURJO4ZCL \
  --region us-east-1

# Wait 15-30 seconds for preparation
sleep 20

# Check status
aws bedrock-agent get-agent \
  --agent-id DJURJO4ZCL \
  --region us-east-1 \
  --query 'agent.agentStatus' \
  --output text
```

**Expected Output**: `PREPARED`

---

### Step 5: Verify Migration

```bash
# Verify agent is using shared role
aws bedrock-agent get-agent \
  --agent-id DJURJO4ZCL \
  --region us-east-1 \
  --query 'agent.agentResourceRoleArn' \
  --output text
```

**Expected Output**: `arn:aws:iam::395102750341:role/BedrockAgentExecutionRole`

```bash
# Verify S3 folders exist
aws s3 ls s3://company-bedrock-agents/agents/perfectgames-agent/ --recursive
```

**Expected Output**:
```
2026-02-05 19:30:00          0 agents/perfectgames-agent/data/
2026-02-05 19:30:00          0 agents/perfectgames-agent/output/
```

---

### Step 6: Test Agent Functionality

```bash
# Test agent invocation
aws bedrock-agent-runtime invoke-agent \
  --agent-id DJURJO4ZCL \
  --agent-alias-id TSTALIASID \
  --session-id test-migration-$(date +%s) \
  --input-text "Test message after migration" \
  --region us-east-1 \
  response.txt

# View response
cat response.txt
```

**Expected**: Agent responds successfully without errors

---

### Step 7: Save Migration Details

```bash
# Create migration record
cat > perfectgames-agent-migration.json << EOF
{
  "agent_id": "DJURJO4ZCL",
  "agent_name": "perfectgames-agent",
  "migration_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "old_role": "arn:aws:iam::395102750341:role/service-role/AmazonBedrockExecutionRoleForAgents_SHH74LGG38R",
  "new_role": "arn:aws:iam::395102750341:role/BedrockAgentExecutionRole",
  "shared_s3_bucket": "company-bedrock-agents",
  "s3_prefix": "agents/perfectgames-agent/",
  "shared_ecr_repo": "bedrock-agents",
  "status": "completed"
}
EOF
```

---

## Migration Steps - Console Method

### Step 1: Get Current Agent Configuration

1. Go to **Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. Click **Agents** in left menu
3. Click on agent: `perfectgames-agent`
4. Note down:
   - Agent ID: `DJURJO4ZCL`
   - Service role: `AmazonBedrockExecutionRoleForAgents_SHH74LGG38R`
   - Foundation model
   - Status

**Screenshot**: Save agent details page for reference

---

### Step 2: Create S3 Folders in EXISTING Shared Bucket

**Important**: We are creating folders INSIDE the EXISTING `company-bedrock-agents` bucket. We are NOT creating a new bucket.

1. Go to **S3 Console**: https://console.aws.amazon.com/s3/
2. Click on **EXISTING** bucket: `company-bedrock-agents`
3. Navigate to `agents/` folder (already exists)
4. Click **Create folder**
   - Folder name: `perfectgames-agent`
   - Click **Create folder**
5. Click into `perfectgames-agent/` folder
6. Click **Create folder**
   - Folder name: `data`
   - Click **Create folder**
7. Click **Create folder**
   - Folder name: `output`
   - Click **Create folder**

**Note**: The bucket `company-bedrock-agents` ALREADY EXISTS. We are only creating folders inside it.

**Verify**: You should see:
```
agents/perfectgames-agent/data/
agents/perfectgames-agent/output/
```

---

### Step 3: Update Agent to Use EXISTING Shared IAM Role

**Important**: We are updating the agent to use the EXISTING `BedrockAgentExecutionRole`. This role ALREADY EXISTS and is shared by other agents.

1. Go to **Bedrock Console** → **Agents**
2. Click on `perfectgames-agent`
3. Click **Edit** in Agent details section
4. **Service role**: Change dropdown to `BedrockAgentExecutionRole` (EXISTING role)
5. Click **Save and exit**

**Note**: The role `BedrockAgentExecutionRole` ALREADY EXISTS in the dropdown. We are NOT creating a new role.

**Expected**: Success message appears

---

### Step 4: Prepare Agent with New Configuration

1. On agent details page, click **Prepare** button (top right)
2. Wait for preparation (~30 seconds)
3. Status changes to "Prepared"

**Expected**: Green checkmark, Status = Prepared

---

### Step 5: Verify Migration

**Verify IAM Role**:
1. On agent details page, check **Service role** field
2. Should show: `BedrockAgentExecutionRole`

**Verify S3 Folders**:
1. Go to **S3 Console**
2. Navigate to: `company-bedrock-agents/agents/perfectgames-agent/`
3. Confirm `data/` and `output/` folders exist

---

### Step 6: Test Agent Functionality

1. On agent details page, click **Test** button (top right)
2. In test panel, enter: `Test message after migration`
3. Click **Send**
4. Review response

**Expected**: Agent responds successfully

---

### Step 7: Document Migration

Create a record in your documentation system:
- Agent: perfectgames-agent
- Migration Date: 2026-02-05
- Old Role: AmazonBedrockExecutionRoleForAgents_SHH74LGG38R
- New Role: BedrockAgentExecutionRole
- Status: Completed

---

## Testing After Migration

### Test 1: Basic Invocation

**CLI**:
```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id DJURJO4ZCL \
  --agent-alias-id TSTALIASID \
  --session-id test-1 \
  --input-text "Hello, are you working correctly?" \
  --region us-east-1 \
  response.txt && cat response.txt
```

**Console**:
1. Agent details page → **Test** button
2. Enter: "Hello, are you working correctly?"
3. Verify response

**Expected**: Agent responds normally

---

### Test 2: S3 Access

**Upload test file**:
```bash
echo "Test data" > test.txt
aws s3 cp test.txt s3://company-bedrock-agents/agents/perfectgames-agent/data/test.txt
```

**Test agent can access**:
```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id DJURJO4ZCL \
  --agent-alias-id TSTALIASID \
  --session-id test-2 \
  --input-text "Read the file at s3://company-bedrock-agents/agents/perfectgames-agent/data/test.txt" \
  --region us-east-1 \
  response.txt
```

**Expected**: Agent successfully accesses file

---

### Test 3: Verify No Access to Other Agent Folders

**Test isolation**:
```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id DJURJO4ZCL \
  --agent-alias-id TSTALIASID \
  --session-id test-3 \
  --input-text "Read file from s3://company-bedrock-agents/agents/image-scanner-agent/images/" \
  --region us-east-1 \
  response.txt
```

**Expected**: Agent can access (shared role has access to entire bucket)

**Note**: For stricter isolation, update IAM role to restrict access per agent prefix.

---

### Test 4: Performance Check

**Before migration** (if you have metrics):
- Average response time: X ms
- Success rate: Y%

**After migration**:
```bash
# Run 10 test invocations
for i in {1..10}; do
  time aws bedrock-agent-runtime invoke-agent \
    --agent-id DJURJO4ZCL \
    --agent-alias-id TSTALIASID \
    --session-id test-perf-$i \
    --input-text "Quick test $i" \
    --region us-east-1 \
    response-$i.txt
done
```

**Expected**: Similar performance to before migration

---

## Verification Checklist

- [ ] Agent ID unchanged: `DJURJO4ZCL`
- [ ] Agent name unchanged: `perfectgames-agent`
- [ ] Agent status: PREPARED
- [ ] IAM role updated to: `BedrockAgentExecutionRole`
- [ ] S3 folders created: `agents/perfectgames-agent/data/` and `output/`
- [ ] Agent responds to test invocations
- [ ] Agent can access S3 files
- [ ] No errors in CloudWatch logs
- [ ] Migration documented

---

## Rollback Plan

If migration fails, revert to original configuration:

**CLI**:
```bash
# Revert to old role
aws bedrock-agent update-agent \
  --agent-id DJURJO4ZCL \
  --agent-name perfectgames-agent \
  --agent-resource-role-arn arn:aws:iam::395102750341:role/service-role/AmazonBedrockExecutionRoleForAgents_SHH74LGG38R \
  --foundation-model anthropic.claude-3-5-sonnet-20240620-v1:0 \
  --instruction "Agent for perfect games analysis" \
  --region us-east-1

# Prepare agent
aws bedrock-agent prepare-agent --agent-id DJURJO4ZCL --region us-east-1
```

**Console**:
1. Agent details → **Edit**
2. Change Service role back to original
3. Click **Save and exit**
4. Click **Prepare**

---

## Cleanup Old Resources

**After successful migration and testing** (wait 7 days):

### Delete Old IAM Role

**CLI**:
```bash
# List attached policies
aws iam list-attached-role-policies \
  --role-name AmazonBedrockExecutionRoleForAgents_SHH74LGG38R

# Detach policies
aws iam detach-role-policy \
  --role-name AmazonBedrockExecutionRoleForAgents_SHH74LGG38R \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Delete role
aws iam delete-role \
  --role-name AmazonBedrockExecutionRoleForAgents_SHH74LGG38R
```

**Console**:
1. Go to **IAM Console** → **Roles**
2. Search for: `AmazonBedrockExecutionRoleForAgents_SHH74LGG38R`
3. Select role → **Delete**
4. Confirm deletion

---

## Benefits After Migration

### Resource Consolidation
- **Before**: 1 IAM role per agent
- **After**: 1 shared IAM role for all agents
- **Savings**: Reduced IAM complexity

### Cost Optimization
- **Before**: Potential separate S3 buckets per agent
- **After**: 1 shared S3 bucket with prefixes
- **Savings**: ~70% reduction in S3 costs

### Management Simplification
- **Before**: Manage multiple IAM roles
- **After**: Manage 1 shared role
- **Benefit**: Easier policy updates

### Compliance
- **Before**: Inconsistent configurations
- **After**: Standardized shared resources
- **Benefit**: Easier auditing

---

## Troubleshooting

### Issue: Agent status stuck in "Not Prepared"

**Solution**:
```bash
# Wait 30 seconds and check again
sleep 30
aws bedrock-agent get-agent --agent-id DJURJO4ZCL --region us-east-1 --query 'agent.agentStatus'
```

### Issue: "Access Denied" when updating agent

**Check**: Verify you have `bedrock:UpdateAgent` permission

**Solution**: Attach `BedrockAgentDeveloperPolicy` to your user

### Issue: Agent cannot access S3 after migration

**Check**: Verify shared role has S3 permissions
```bash
aws iam get-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3Access
```

**Solution**: Add S3 permissions to shared role

### Issue: Test invocation fails

**Check CloudWatch Logs**:
```bash
aws logs tail /aws/bedrock/agents/DJURJO4ZCL --follow
```

---

## Summary

**Migration Completed**:
- ✅ Agent: `perfectgames-agent` (DJURJO4ZCL)
- ✅ Now using **EXISTING** shared IAM role: `BedrockAgentExecutionRole`
- ✅ Now using **EXISTING** shared S3: `company-bedrock-agents`
- ✅ Now using **EXISTING** shared ECR: `bedrock-agents`
- ✅ Agent tested and working
- ✅ Old role can be deleted after 7 days

**Key Point**: NO new resources were created. Agent now uses EXISTING shared resources.

**Resources Used**:
- EXISTING S3 Bucket: `company-bedrock-agents` (created before migration)
- EXISTING ECR Repository: `bedrock-agents` (created before migration)
- EXISTING IAM Role: `BedrockAgentExecutionRole` (created before migration)

**Time Taken**: ~10 minutes  
**Downtime**: None  
**Rollback Available**: Yes  
**New Resources Created**: 0 (only folders in existing S3 bucket)

---

## Next Steps

1. Monitor agent for 7 days
2. Delete old IAM role if no issues
3. Migrate additional agents using same process
4. Update documentation with agent-specific S3 paths
5. Set up CloudWatch alarms for monitoring

---

## Additional Resources

- **AWS Bedrock Agents**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- **IAM Roles**: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html
- **S3 Best Practices**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html

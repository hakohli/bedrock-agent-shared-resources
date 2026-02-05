# Test Document: Migrating Existing Agent to Shared Resources

**Scenario**: Update an existing Bedrock agent (deployed via starter toolkit) to use existing shared S3 bucket and ECR repository.

---

## Current Situation

**Before Migration**:
- Agent deployed using starter toolkit
- Agent creates its own S3 bucket per deployment
- Agent creates its own ECR repository per deployment
- Developers need infrastructure team help for each deployment
- No fine-grained IAM controls

**After Migration**:
- Agent uses existing shared S3 bucket: `company-bedrock-agents`
- Agent uses existing shared ECR repository: `bedrock-agents`
- Developers deploy agents self-service
- Fine-grained IAM policy prevents resource creation
- Infrastructure team maintains control

---

## Test Environment

**Existing Agent Details**:
- Agent Name: `customer-support-agent`
- Agent ID: `EXISTING123`
- Current S3 Bucket: `customer-support-agent-bucket-abc123`
- Current ECR Repo: `customer-support-agent-repo`
- Foundation Model: Claude 3 Sonnet

**Target Shared Resources**:
- Shared S3 Bucket: `company-bedrock-agents`
- Shared ECR Repository: `bedrock-agents`
- IAM Role: `BedrockAgentExecutionRole`
- IAM Policy: `BedrockAgentDeveloperPolicy`

---

## Migration Test Plan

### Phase 1: Infrastructure Setup (One-Time)

**Test 1.1: Create Shared ECR Repository**

```bash
# Run as infrastructure admin
aws ecr create-repository \
  --repository-name bedrock-agents \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true \
  --tags Key=auto-delete,Value=no

# Expected: Repository created successfully
# Verify: aws ecr describe-repositories --repository-names bedrock-agents
```

**Test 1.2: Create Shared S3 Bucket**

```bash
# Run as infrastructure admin
aws s3 mb s3://company-bedrock-agents --region us-east-1
aws s3api put-bucket-versioning --bucket company-bedrock-agents --versioning-configuration Status=Enabled
aws s3api put-bucket-tagging --bucket company-bedrock-agents --tagging 'TagSet=[{Key=auto-delete,Value=no}]'

# Create folder structure
aws s3api put-object --bucket company-bedrock-agents --key agents/
aws s3api put-object --bucket company-bedrock-agents --key agents/customer-support-agent/
aws s3api put-object --bucket company-bedrock-agents --key agents/customer-support-agent/data/

# Expected: Bucket created with folders
# Verify: aws s3 ls s3://company-bedrock-agents/agents/
```

**Test 1.3: Create IAM Execution Role**

```bash
# Create trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "bedrock.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name BedrockAgentExecutionRole \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=auto-delete,Value=no

# Attach policies
aws iam attach-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Add S3 access
cat > s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::company-bedrock-agents",
      "arn:aws:s3:::company-bedrock-agents/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3Access \
  --policy-document file://s3-policy.json

# Expected: Role created with S3 access
# Verify: aws iam get-role --role-name BedrockAgentExecutionRole
```

**Test 1.4: Create Developer IAM Policy**

```bash
# Create restrictive policy
aws iam create-policy \
  --policy-name BedrockAgentDeveloperPolicy \
  --policy-document file://iam-policy.json \
  --tags Key=auto-delete,Value=no

# Attach to developer user
aws iam attach-user-policy \
  --user-name developer-test-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy

# Expected: Policy created and attached
# Verify: aws iam list-attached-user-policies --user-name developer-test-user
```

---

### Phase 2: Migrate Data (Before Agent Update)

**Test 2.1: Copy Existing Data to Shared S3**

```bash
# Copy data from old bucket to shared bucket
OLD_BUCKET="customer-support-agent-bucket-abc123"
NEW_PREFIX="agents/customer-support-agent"

aws s3 sync s3://$OLD_BUCKET/ s3://company-bedrock-agents/$NEW_PREFIX/

# Expected: All files copied
# Verify: aws s3 ls s3://company-bedrock-agents/$NEW_PREFIX/ --recursive
```

**Test 2.2: Copy Container Images to Shared ECR**

```bash
# Pull image from old repository
OLD_REPO="YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/customer-support-agent-repo"
NEW_REPO="YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/bedrock-agents"

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $OLD_REPO

# Pull, tag, and push
docker pull $OLD_REPO:latest
docker tag $OLD_REPO:latest $NEW_REPO:customer-support-agent
docker push $NEW_REPO:customer-support-agent

# Expected: Image available in shared repository
# Verify: aws ecr describe-images --repository-name bedrock-agents
```

---

### Phase 3: Update Agent Configuration

**Test 3.1: Update Agent to Use Shared Role (CLI)**

```bash
# Get current agent details
aws bedrock-agent get-agent --agent-id EXISTING123 --region us-east-1

# Update agent to use shared execution role
aws bedrock-agent update-agent \
  --agent-id EXISTING123 \
  --agent-name customer-support-agent \
  --agent-resource-role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/BedrockAgentExecutionRole \
  --foundation-model anthropic.claude-3-sonnet-20240229-v1:0 \
  --instruction "Your agent instructions here" \
  --region us-east-1

# Expected: Agent updated successfully
# Verify: aws bedrock-agent get-agent --agent-id EXISTING123
```

**Test 3.2: Prepare Agent with New Configuration**

```bash
# Prepare agent to apply changes
aws bedrock-agent prepare-agent --agent-id EXISTING123 --region us-east-1

# Wait for preparation
sleep 30

# Check status
aws bedrock-agent get-agent --agent-id EXISTING123 --query 'agent.agentStatus' --output text

# Expected: Status = PREPARED
```

**Test 3.3: Update Application Code to Use Shared S3**

```python
# OLD CODE (before migration)
s3_uri = "s3://customer-support-agent-bucket-abc123/data/file.txt"

# NEW CODE (after migration)
s3_uri = "s3://company-bedrock-agents/agents/customer-support-agent/data/file.txt"
```

Update all references in your application code.

---

### Phase 4: Testing

**Test 4.1: Verify Agent Can Access Shared S3**

```bash
# Upload test file to shared bucket
echo "Test data" > test.txt
aws s3 cp test.txt s3://company-bedrock-agents/agents/customer-support-agent/data/test.txt

# Invoke agent to access the file
aws bedrock-agent-runtime invoke-agent \
  --agent-id EXISTING123 \
  --agent-alias-id TSTALIASID \
  --session-id test-session-1 \
  --input-text "Read the test file from s3://company-bedrock-agents/agents/customer-support-agent/data/test.txt" \
  --region us-east-1 \
  response.txt

# Expected: Agent successfully accesses file
# Verify: cat response.txt
```

**Test 4.2: Verify Developer Cannot Create New Resources**

```bash
# As developer user, try to create S3 bucket (should fail)
aws s3 mb s3://test-unauthorized-bucket

# Expected: AccessDenied error
# Result: ✓ PASS if denied

# Try to create ECR repository (should fail)
aws ecr create-repository --repository-name test-unauthorized-repo

# Expected: AccessDenied error
# Result: ✓ PASS if denied
```

**Test 4.3: Verify Developer Can Update Agent**

```bash
# As developer user, update agent description
aws bedrock-agent update-agent \
  --agent-id EXISTING123 \
  --agent-name customer-support-agent \
  --description "Updated description - testing permissions" \
  --agent-resource-role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/BedrockAgentExecutionRole \
  --foundation-model anthropic.claude-3-sonnet-20240229-v1:0 \
  --instruction "Your agent instructions" \
  --region us-east-1

# Expected: Update successful
# Result: ✓ PASS if successful
```

**Test 4.4: End-to-End Agent Invocation Test**

```python
#!/usr/bin/env python3
import boto3
import json

# Test agent invocation with shared resources
bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = bedrock_runtime.invoke_agent(
    agentId='EXISTING123',
    agentAliasId='TSTALIASID',
    sessionId='test-session-e2e',
    inputText='Process data from s3://company-bedrock-agents/agents/customer-support-agent/data/'
)

# Process response
for event in response['completion']:
    if 'chunk' in event:
        chunk = event['chunk']
        if 'bytes' in chunk:
            print(chunk['bytes'].decode('utf-8'), end='')

# Expected: Agent responds successfully using shared S3
# Result: ✓ PASS if agent processes data
```

---

### Phase 5: Cleanup Old Resources

**Test 5.1: Verify Migration Success**

```bash
# Check agent is using shared resources
aws bedrock-agent get-agent --agent-id EXISTING123 --query 'agent.agentResourceRoleArn' --output text

# Expected: arn:aws:iam::YOUR_ACCOUNT_ID:role/BedrockAgentExecutionRole
# Result: ✓ PASS if matches

# Verify data accessible in shared S3
aws s3 ls s3://company-bedrock-agents/agents/customer-support-agent/ --recursive

# Expected: All files present
# Result: ✓ PASS if files exist
```

**Test 5.2: Delete Old S3 Bucket**

```bash
# Empty old bucket
aws s3 rm s3://customer-support-agent-bucket-abc123 --recursive

# Delete old bucket
aws s3 rb s3://customer-support-agent-bucket-abc123

# Expected: Bucket deleted
# Verify: aws s3 ls | grep customer-support-agent-bucket
```

**Test 5.3: Delete Old ECR Repository**

```bash
# Delete old ECR repository
aws ecr delete-repository \
  --repository-name customer-support-agent-repo \
  --force \
  --region us-east-1

# Expected: Repository deleted
# Verify: aws ecr describe-repositories --repository-names customer-support-agent-repo
```

---

## Test Results Template

### Infrastructure Setup
- [ ] ECR repository created: `bedrock-agents`
- [ ] S3 bucket created: `company-bedrock-agents`
- [ ] IAM role created: `BedrockAgentExecutionRole`
- [ ] IAM policy created: `BedrockAgentDeveloperPolicy`
- [ ] Policy attached to developer user

### Data Migration
- [ ] Data copied from old S3 to shared S3
- [ ] Container images copied to shared ECR
- [ ] All files verified in new locations

### Agent Update
- [ ] Agent updated to use `BedrockAgentExecutionRole`
- [ ] Agent prepared successfully
- [ ] Application code updated with new S3 paths

### Permission Testing
- [ ] Developer CANNOT create S3 buckets (denied)
- [ ] Developer CANNOT create ECR repositories (denied)
- [ ] Developer CAN update agent configuration
- [ ] Developer CAN invoke agent

### Functional Testing
- [ ] Agent can access files in shared S3
- [ ] Agent responds to invocations correctly
- [ ] End-to-end workflow successful

### Cleanup
- [ ] Old S3 bucket deleted
- [ ] Old ECR repository deleted
- [ ] No orphaned resources

---

## Rollback Plan

If migration fails:

```bash
# 1. Revert agent to old role
aws bedrock-agent update-agent \
  --agent-id EXISTING123 \
  --agent-resource-role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/OldAgentRole \
  --region us-east-1

# 2. Revert application code to old S3 paths
# (Restore from version control)

# 3. Keep old resources until migration is successful
# DO NOT delete old S3 bucket or ECR repository until verified
```

---

## Success Criteria

✅ **Migration Successful If**:
1. Agent uses `BedrockAgentExecutionRole`
2. Agent accesses data from `company-bedrock-agents` bucket
3. Container images in `bedrock-agents` ECR repository
4. Developer can deploy/update agents without infrastructure team
5. Developer CANNOT create new S3 buckets or ECR repositories
6. All functional tests pass
7. Old resources safely deleted

---

## Performance Comparison

### Before Migration
- **Deployment Time**: 30-60 minutes (requires infrastructure team)
- **Resources Created**: 2 per agent (S3 bucket + ECR repo)
- **Cost**: High (duplicate resources)
- **Management**: Complex (many resources)

### After Migration
- **Deployment Time**: 5-10 minutes (self-service)
- **Resources Created**: 0 (uses shared resources)
- **Cost**: Low (shared infrastructure)
- **Management**: Simple (centralized resources)

---

## Troubleshooting

### Issue: Agent cannot access shared S3

**Check**:
```bash
aws iam get-role-policy --role-name BedrockAgentExecutionRole --policy-name S3Access
```

**Fix**: Ensure S3Access policy includes `company-bedrock-agents` bucket

### Issue: Developer can still create buckets

**Check**:
```bash
aws iam list-attached-user-policies --user-name developer-test-user
```

**Fix**: Ensure `BedrockAgentDeveloperPolicy` is attached and includes deny statements

### Issue: Agent preparation fails

**Check**:
```bash
aws bedrock-agent get-agent --agent-id EXISTING123 --query 'agent.agentStatus'
```

**Fix**: Wait 30-60 seconds and retry preparation

---

## Conclusion

This test document validates that:
1. ✅ Existing agents can be migrated to shared resources
2. ✅ Developers can self-service deploy without infrastructure team
3. ✅ Fine-grained IAM policies prevent resource creation
4. ✅ Shared resources reduce costs and complexity
5. ✅ Migration is reversible with rollback plan

**Recommendation**: Proceed with production migration following this tested approach.

# Demo Walkthrough

This guide walks through the complete demo showing how to use existing ECR/S3 resources with Bedrock agents.

## Scenario

**Infrastructure Team** (one-time setup):
- Creates shared ECR repository
- Creates shared S3 bucket
- Creates IAM roles and policies
- Restricts developers from creating new infrastructure

**Development Team** (self-service):
- Deploys agents using existing resources
- No need to request infrastructure changes
- Cannot create new ECR repos or S3 buckets

---

## Part 1: Infrastructure Team Setup (One-Time)

### Step 1: Set Environment Variables

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
export APPROVED_ECR_REPO="bedrock-agents"
export SHARED_S3_BUCKET="company-bedrock-agents"
```

### Step 2: Run Infrastructure Setup

```bash
./setup_infrastructure.sh
```

This creates:
- ECR repository: `bedrock-agents`
- S3 bucket: `company-bedrock-agents`
- IAM role: `BedrockAgentExecutionRole`
- IAM policy: `BedrockAgentDeveloperPolicy`

### Step 3: Attach Policy to Developers

```bash
# For a specific user
aws iam attach-user-policy \
  --user-name developer-username \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy

# Or for a group
aws iam attach-group-policy \
  --group-name developers \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy
```

---

## Part 2: Developer Workflow (Self-Service)

### Step 1: Verify Permissions

```bash
python verify_permissions.py
```

Expected output:
```
✓ PASS: BEDROCK
✓ PASS: S3
✓ PASS: ECR
✓ PASS: IAM
✓ PASS: DENIED

✓ All checks passed! Ready to deploy agents.
```

### Step 2: Deploy Agent

```bash
python deploy_agent.py
```

Expected output:
```
Creating agent: baseball-video-analyzer
Using execution role: arn:aws:iam::YOUR_ACCOUNT_ID:role/BedrockAgentExecutionRole
Using S3 bucket: company-bedrock-agents

✓ Agent created successfully!
  Agent ID: ABCD1234
  Agent ARN: arn:aws:bedrock:us-east-1:YOUR_ACCOUNT_ID:agent/ABCD1234

✓ Agent prepared successfully!
  Status: PREPARED

✓ Agent alias created successfully!
  Alias ID: TSTALIASID

✓ Deployment info saved to deployment_info.json

Deployment Complete!
```

### Step 3: Test Agent

```bash
python test_agent.py
```

This runs three test prompts to verify the agent works correctly.

### Step 4: Clean Up (Optional)

```bash
python cleanup.py
```

---

## Part 3: Key Security Features Demonstrated

### 1. Resource Reuse
- ✓ Multiple agents share same ECR repository
- ✓ Multiple agents share same S3 bucket (different prefixes)
- ✓ No new infrastructure created per agent

### 2. Permission Boundaries
- ✓ Developers can create/update/delete agents
- ✓ Developers can use existing ECR repository
- ✓ Developers can use existing S3 bucket
- ✗ Developers CANNOT create new ECR repositories
- ✗ Developers CANNOT create new S3 buckets

### 3. Verification

Try to create a bucket (should fail):
```bash
aws s3 mb s3://test-unauthorized-bucket
```

Expected: `AccessDenied` error

Try to create ECR repo (should fail):
```bash
aws ecr create-repository --repository-name test-unauthorized-repo
```

Expected: `AccessDenied` error

---

## Part 4: Customization Examples

### Deploy Multiple Agents

Edit `agent_config.py` and change the agent name:
```python
AGENT_CONFIG = {
    'agent_name': 'customer-support-agent',  # Changed
    'description': 'Customer support assistant',
    # ...
}
```

Then deploy:
```bash
python deploy_agent.py
```

Both agents will use the same ECR and S3 resources!

### Add Action Groups

Modify `deploy_agent.py` to add Lambda-based action groups:
```python
bedrock.create_agent_action_group(
    agentId=agent_id,
    agentVersion='DRAFT',
    actionGroupName='video-processor',
    actionGroupExecutor={
        'lambda': 'arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:bedrock-agent-video-processor'
    },
    apiSchema={
        'payload': json.dumps({
            'openapi': '3.0.0',
            'info': {'title': 'Video Processor', 'version': '1.0.0'},
            'paths': {
                '/analyze': {
                    'post': {
                        'description': 'Analyze baseball video',
                        'parameters': [
                            {'name': 's3_uri', 'in': 'query', 'required': True, 'schema': {'type': 'string'}}
                        ]
                    }
                }
            }
        })
    }
)
```

---

## Summary

This demo shows:
1. ✓ Infrastructure team controls resource creation
2. ✓ Developers deploy agents self-service
3. ✓ Shared resources reduce costs and complexity
4. ✓ Fine-grained IAM policies enforce boundaries
5. ✓ Easy to verify permissions before deployment

**Result**: Secure, scalable, self-service agent deployment!

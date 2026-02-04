# Bedrock Agent Demo - Using Existing Resources

Complete guide for deploying Amazon Bedrock agents using pre-approved ECR repositories and shared S3 buckets with fine-grained IAM controls.

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [Prerequisites](#prerequisites)
- [Part 1: Infrastructure Team Setup](#part-1-infrastructure-team-setup)
- [Part 2: Developer Workflow](#part-2-developer-workflow)
- [Part 3: Testing & Verification](#part-3-testing--verification)
- [Part 4: Cleanup](#part-4-cleanup)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Cost Optimization](#cost-optimization)

---

## Overview

This demo demonstrates how to enable self-service Bedrock agent deployment while maintaining strict infrastructure controls. Developers can deploy and manage agents without requiring infrastructure team intervention, while being restricted from creating new ECR repositories or S3 buckets.

### Key Benefits

- ✅ **Self-Service**: Developers deploy agents independently
- ✅ **Cost Efficient**: Shared infrastructure reduces resource duplication
- ✅ **Secure**: Fine-grained IAM policies enforce boundaries
- ✅ **Scalable**: Support multiple agents with single infrastructure
- ✅ **Compliant**: Pre-approved resources meet security requirements

---

## Problem Statement

Organizations often face these challenges with Bedrock agents:

1. **Resource Sprawl**: Each agent creates separate ECR repos and S3 buckets
2. **Security Concerns**: Developers need restricted access to approved resources only
3. **Manual Overhead**: Infrastructure team bottleneck for every deployment
4. **Cost Issues**: Duplicate infrastructure increases AWS costs

### This Solution Provides

- Single shared ECR repository for all agent containers
- Single shared S3 bucket with per-agent prefixes for isolation
- IAM policy allowing agent operations but denying resource creation
- Self-service deployment scripts for developers

---

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Team                       │
│                      (One-Time Setup)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Shared Resources (Account 395102750341) │
        ├─────────────────────────────────────────┤
        │  • ECR: bedrock-agents                  │
        │  • S3: company-bedrock-agents           │
        │  • IAM Role: BedrockAgentExecutionRole  │
        │  • IAM Policy: BedrockAgentDeveloper... │
        └─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Developer Team                          │
│                   (Self-Service Deploy)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Bedrock Agent Deployed          │
        ├─────────────────────────────────────────┤
        │  Agent ID: R9ORLA8SGF                   │
        │  Uses: Existing ECR + S3                │
        │  Isolated: /agents/{agent-name}/        │
        └─────────────────────────────────────────┘
```

---

## Prerequisites

### AWS Account Requirements

- **AWS Account ID**: 395102750341
- **Region**: us-east-1 (or your preferred region)
- **Bedrock Access**: Enabled in your account
- **Model Access**: Anthropic Claude 3 Sonnet enabled

### Required Permissions (Infrastructure Team)

- Full IAM permissions (create roles, policies)
- ECR repository creation
- S3 bucket creation
- Bedrock agent access

### Required Tools

- AWS CLI v2.x or later
- Python 3.9 or later
- boto3 library (`pip install boto3`)
- Git (optional, for version control)

### Verify Prerequisites

```bash
# Check AWS CLI
aws --version

# Check Python
python3 --version

# Check boto3
python3 -c "import boto3; print(boto3.__version__)"

# Check AWS credentials
aws sts get-caller-identity
```

---

## Part 1: Infrastructure Team Setup

**Who**: Infrastructure/Platform team with admin access  
**When**: One-time setup  
**Duration**: ~5 minutes

### Step 1: Clone or Download Demo Files

```bash
cd /Users/hakohli/bedrock-agent-demo
```

### Step 2: Review Configuration Files

**iam-policy.json** - Developer permissions policy:
- ✅ Allows: Bedrock agent operations, ECR read/write, S3 read/write
- ❌ Denies: ECR repository creation, S3 bucket creation

**trust-policy.json** - Agent execution role trust policy:
- Allows Bedrock service to assume the role

**agent_config.py** - Agent configuration:
- Agent name, description, foundation model
- S3 paths within shared bucket

### Step 3: Set Environment Variables

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="395102750341"
export APPROVED_ECR_REPO="bedrock-agents"
export SHARED_S3_BUCKET="company-bedrock-agents"
```

**Optional**: Add to `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export AWS_REGION="us-east-1"' >> ~/.bashrc
echo 'export AWS_ACCOUNT_ID="395102750341"' >> ~/.bashrc
echo 'export APPROVED_ECR_REPO="bedrock-agents"' >> ~/.bashrc
echo 'export SHARED_S3_BUCKET="company-bedrock-agents"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Run Infrastructure Setup

```bash
chmod +x setup_infrastructure.sh
./setup_infrastructure.sh
```

**This script creates**:

1. **ECR Repository**: `bedrock-agents`
   - Image scanning enabled
   - AES256 encryption
   - Repository URI: `395102750341.dkr.ecr.us-east-1.amazonaws.com/bedrock-agents`

2. **S3 Bucket**: `company-bedrock-agents`
   - Versioning enabled
   - Server-side encryption (AES256)
   - Folder structure: `/agents/{agent-name}/videos/` and `/artifacts/`

3. **IAM Role**: `BedrockAgentExecutionRole`
   - Trust policy for bedrock.amazonaws.com
   - AmazonBedrockFullAccess policy attached
   - S3 access to shared bucket

4. **IAM Policy**: `BedrockAgentDeveloperPolicy`
   - Allows Bedrock agent operations
   - Allows using existing ECR/S3
   - Denies creating new ECR/S3 resources

### Step 5: Grant Developer Access

Attach the policy to developer users or groups:

```bash
# For individual user
aws iam attach-user-policy \
  --user-name developer-username \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy

# For developer group
aws iam attach-group-policy \
  --group-name developers \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy

# For IAM role (if using role-based access)
aws iam attach-role-policy \
  --role-name DeveloperRole \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy
```

### Step 6: Verify Infrastructure

```bash
# Check ECR repository
aws ecr describe-repositories --repository-names bedrock-agents

# Check S3 bucket
aws s3 ls s3://company-bedrock-agents/

# Check IAM role
aws iam get-role --role-name BedrockAgentExecutionRole

# Check IAM policy
aws iam get-policy --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy
```

**✅ Infrastructure setup complete!**

---

## Part 2: Developer Workflow

**Who**: Developers with BedrockAgentDeveloperPolicy attached  
**When**: Anytime they need to deploy an agent  
**Duration**: ~2 minutes

### Step 1: Verify Permissions

Before deploying, verify you have the correct permissions:

```bash
cd /Users/hakohli/bedrock-agent-demo
python3 verify_permissions.py
```

**Expected output**:
```
✓ PASS: BEDROCK
✓ PASS: S3
✓ PASS: ECR
✓ PASS: IAM
✓ PASS: DENIED (resource creation correctly blocked)
```

**If checks fail**: Contact infrastructure team to attach BedrockAgentDeveloperPolicy

### Step 2: Configure Your Agent

Edit `agent_config.py` to customize your agent:

```python
AGENT_CONFIG = {
    'agent_name': 'baseball-video-analyzer',  # Change this
    'description': 'Your agent description',
    'instruction': '''Your agent instructions here''',
    'foundation_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'idle_session_ttl': 600
}
```

**Agent naming conventions**:
- Use lowercase with hyphens
- Be descriptive: `customer-support-agent`, `data-analyzer-agent`
- Avoid special characters

### Step 3: Deploy Agent

```bash
python3 deploy_agent.py
```

**What happens**:
1. Creates Bedrock agent with your configuration
2. Uses existing `BedrockAgentExecutionRole`
3. Prepares agent (compiles and validates)
4. Creates production alias
5. Saves deployment info to `deployment_info.json`

**Expected output**:
```
============================================================
Bedrock Agent Deployment Demo
Using Existing ECR and S3 Resources
============================================================
Creating agent: baseball-video-analyzer
Using execution role: arn:aws:iam::395102750341:role/BedrockAgentExecutionRole
Using S3 bucket: company-bedrock-agents

✓ Agent created successfully!
  Agent ID: R9ORLA8SGF
  Agent ARN: arn:aws:bedrock:us-east-1:395102750341:agent/R9ORLA8SGF

✓ Agent prepared successfully!
  Status: PREPARED

✓ Agent alias created successfully!
  Alias ID: 5DRROVGWEI

✓ Deployment info saved to deployment_info.json

Deployment Complete!
```

### Step 4: Note Your Agent Details

The `deployment_info.json` file contains:
```json
{
  "agent_id": "R9ORLA8SGF",
  "alias_id": "5DRROVGWEI",
  "agent_name": "baseball-video-analyzer",
  "region": "us-east-1",
  "account_id": "395102750341",
  "s3_bucket": "company-bedrock-agents"
}
```

**Save this file** - you'll need it for testing and management.

---

## Part 3: Testing & Verification

### Test Your Agent

```bash
python3 test_agent.py
```

This runs three test prompts:
1. Query agent capabilities
2. Request video analysis
3. Ask about scoreboard information

**Sample output**:
```
============================================================
Bedrock Agent Test
============================================================

Agent ID: R9ORLA8SGF
Alias ID: 5DRROVGWEI
Agent Name: baseball-video-analyzer

============================================================
Test 1/3
============================================================

Invoking agent with prompt: What kind of information can you extract from baseball videos?
------------------------------------------------------------
From baseball video footage, I can extract the following information:

- Scoreboard information such as the teams playing, current scores, inning, and ball/strike count
- Player identification including jersey numbers and positions on the field
- Key plays and events like hits, strikeouts, and fielding actions
------------------------------------------------------------
```

### Verify Resource Usage

```bash
# Check S3 structure
aws s3 ls s3://company-bedrock-agents/agents/ --recursive

# Check agent in Bedrock
aws bedrock-agent get-agent --agent-id R9ORLA8SGF

# View in AWS Console
# https://console.aws.amazon.com/bedrock/home?region=us-east-1#/agents/R9ORLA8SGF
```

### Custom Testing

Create your own test script:

```python
import boto3
import json

# Load deployment info
with open('deployment_info.json', 'r') as f:
    info = json.load(f)

# Invoke agent
bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
response = bedrock_runtime.invoke_agent(
    agentId=info['agent_id'],
    agentAliasId=info['alias_id'],
    sessionId='my-test-session',
    inputText='Your prompt here'
)

# Process response
for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='')
```

---

## Part 4: Cleanup

### Delete Agent Only (Keep Infrastructure)

```bash
python3 cleanup.py
```

This deletes the agent but preserves shared infrastructure (ECR, S3, IAM).

### Delete Everything (Infrastructure Team Only)

```bash
# Delete agent first
python3 cleanup.py

# Delete IAM policy attachments
aws iam detach-user-policy \
  --user-name developer-username \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy

# Delete IAM policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::395102750341:policy/BedrockAgentDeveloperPolicy

# Delete IAM role policies
aws iam detach-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam delete-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name S3Access

# Delete IAM role
aws iam delete-role --role-name BedrockAgentExecutionRole

# Empty and delete S3 bucket
aws s3 rm s3://company-bedrock-agents --recursive
aws s3 rb s3://company-bedrock-agents

# Delete ECR repository
aws ecr delete-repository \
  --repository-name bedrock-agents \
  --force
```

---

## Troubleshooting

### Issue: "AccessDenied" when deploying agent

**Cause**: BedrockAgentDeveloperPolicy not attached to your user/role

**Solution**:
```bash
# Check current policies
aws iam list-attached-user-policies --user-name $(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)

# Contact infrastructure team to attach policy
```

### Issue: "Agent still preparing" error

**Cause**: Agent preparation takes 10-30 seconds

**Solution**: Wait and retry:
```bash
sleep 15
python3 deploy_agent.py
```

### Issue: "Bucket does not exist"

**Cause**: Infrastructure setup not completed

**Solution**:
```bash
# Verify bucket exists
aws s3 ls s3://company-bedrock-agents/

# If not, run infrastructure setup
./setup_infrastructure.sh
```

### Issue: "Model access denied"

**Cause**: Claude 3 Sonnet not enabled in Bedrock

**Solution**:
1. Go to AWS Console → Bedrock → Model access
2. Request access to Anthropic Claude 3 Sonnet
3. Wait for approval (usually instant)

### Issue: Python version warnings

**Cause**: Using Python 3.9 (deprecated)

**Solution**:
```bash
# Install Python 3.10+
brew install python@3.10  # macOS
# or
sudo apt install python3.10  # Linux

# Use newer Python
python3.10 deploy_agent.py
```

---

## Security Considerations

### IAM Policy Design

The `BedrockAgentDeveloperPolicy` follows least-privilege principles:

**Allowed**:
- Create/update/delete Bedrock agents
- Read/write to approved ECR repository only
- Read/write to approved S3 bucket only
- Pass BedrockAgentExecutionRole to Bedrock service

**Denied**:
- Create new ECR repositories
- Create new S3 buckets
- Modify bucket policies
- Access other AWS resources

### S3 Isolation

Each agent gets isolated prefix:
```
s3://company-bedrock-agents/
  └── agents/
      ├── baseball-video-analyzer/
      │   ├── videos/
      │   └── artifacts/
      └── customer-support-agent/
          ├── videos/
          └── artifacts/
```

**Best practice**: Add S3 bucket policies for additional isolation if needed.

### ECR Security

- Image scanning enabled (detects vulnerabilities)
- Encryption at rest (AES256)
- Access limited to approved repository only

### Secrets Management

**Never hardcode**:
- API keys
- Database passwords
- Access tokens

**Use instead**:
- AWS Secrets Manager
- AWS Systems Manager Parameter Store
- Environment variables (for non-sensitive config)

---

## Cost Optimization

### Shared Infrastructure Savings

**Without this approach** (per agent):
- ECR repository: $0.10/GB/month
- S3 bucket: $0.023/GB/month
- 10 agents = 10x costs

**With this approach**:
- 1 ECR repository shared
- 1 S3 bucket shared
- ~70% cost reduction

### Bedrock Agent Costs

- **Model invocation**: Pay per token
- **Agent runtime**: No additional charge
- **Storage**: S3 standard pricing

**Estimate costs**: https://calculator.aws

### Cost Monitoring

```bash
# Check S3 storage usage
aws s3 ls s3://company-bedrock-agents --recursive --summarize

# Check ECR storage
aws ecr describe-repositories --repository-names bedrock-agents \
  --query 'repositories[0].repositoryUri'

# Set up billing alerts in AWS Console
```

---

## Files Reference

| File | Purpose | Used By |
|------|---------|---------|
| `setup_infrastructure.sh` | Create shared resources | Infrastructure Team |
| `iam-policy.json` | Developer permissions | Infrastructure Team |
| `trust-policy.json` | Agent execution role | Infrastructure Team |
| `agent_config.py` | Agent configuration | Developers |
| `deploy_agent.py` | Deploy agent | Developers |
| `test_agent.py` | Test agent | Developers |
| `verify_permissions.py` | Check IAM permissions | Developers |
| `cleanup.py` | Delete agent | Developers |
| `deployment_info.json` | Agent details (generated) | Auto-generated |

---

## Next Steps

1. **Customize agent**: Modify `agent_config.py` for your use case
2. **Add action groups**: Integrate Lambda functions for custom actions
3. **Add knowledge bases**: Connect to data sources for RAG
4. **Monitor usage**: Set up CloudWatch dashboards
5. **Scale**: Deploy multiple agents using same infrastructure

---

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/bedrock/
- **Bedrock Agents Guide**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

---

## License

This demo is provided as-is for educational purposes.

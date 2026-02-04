# Quick Start Guide

## For Infrastructure Team

1. **One-time setup** (5 minutes):
   ```bash
   cd bedrock-agent-demo
   export AWS_REGION="us-east-1"
   export AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
   ./setup_infrastructure.sh
   ```

2. **Grant developer access**:
   ```bash
   aws iam attach-user-policy \
     --user-name <developer-name> \
     --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy
   ```

## For Developers

1. **Verify permissions**:
   ```bash
   cd bedrock-agent-demo
   python verify_permissions.py
   ```

2. **Deploy agent**:
   ```bash
   python deploy_agent.py
   ```

3. **Test agent**:
   ```bash
   python test_agent.py
   ```

4. **Clean up** (optional):
   ```bash
   python cleanup.py
   ```

## What You Get

- ✓ Shared ECR repository for all agents
- ✓ Shared S3 bucket with per-agent prefixes
- ✓ Self-service agent deployment
- ✓ No ability to create new infrastructure
- ✓ Full Bedrock agent capabilities

## Files Overview

| File | Purpose | Who Uses |
|------|---------|----------|
| `setup_infrastructure.sh` | Create shared resources | Infrastructure Team |
| `iam-policy.json` | Developer permissions | Infrastructure Team |
| `trust-policy.json` | Agent execution role | Infrastructure Team |
| `agent_config.py` | Agent configuration | Developers |
| `deploy_agent.py` | Deploy agent | Developers |
| `test_agent.py` | Test agent | Developers |
| `verify_permissions.py` | Check permissions | Developers |
| `cleanup.py` | Delete agent | Developers |

## Support

- Infrastructure issues: Contact infrastructure team
- Agent deployment issues: Check `verify_permissions.py` output
- Agent behavior issues: Check CloudWatch logs

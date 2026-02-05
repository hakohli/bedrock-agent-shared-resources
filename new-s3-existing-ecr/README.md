# Bedrock Agent Demo - New S3 Bucket + Existing ECR

Deploy Amazon Bedrock agents using a **new dedicated S3 bucket per agent** while sharing a common ECR repository.

---

## Scenario

**Use Case**: You want agents to have isolated S3 buckets for data separation, but share a common ECR repository for container images.

**What's Shared**: ECR repository  
**What's Per-Agent**: S3 bucket

---

## Architecture

```
┌─────────────────────────────────────────┐
│     Shared Infrastructure (Once)        │
├─────────────────────────────────────────┤
│  • ECR: bedrock-agents (shared)         │
│  • IAM Role: BedrockAgentExecutionRole  │
│  • IAM Policy: BedrockAgentPolicy       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│        Per-Agent Resources              │
├─────────────────────────────────────────┤
│  • S3: agent-name-data-bucket           │
│  • Bedrock Agent                        │
└─────────────────────────────────────────┘
```

---

## Key Differences from Shared S3 Approach

| Aspect | Shared S3 | New S3 Per Agent |
|--------|-----------|------------------|
| **S3 Buckets** | 1 shared bucket | 1 bucket per agent |
| **Data Isolation** | Prefix-based | Bucket-level |
| **Permissions** | Cannot create buckets | Can create buckets |
| **Cost** | Lower (1 bucket) | Higher (multiple buckets) |
| **Management** | Simpler | More buckets to manage |
| **Use Case** | Cost-effective, simple | Strong isolation needed |

---

## When to Use This Approach

✅ **Use New S3 Per Agent When**:
- Strong data isolation requirements
- Different compliance needs per agent
- Separate billing/cost tracking per agent
- Different retention policies per agent
- Different encryption keys per agent

❌ **Use Shared S3 When**:
- Cost optimization is priority
- Simple data isolation via prefixes is sufficient
- Centralized data management preferred
- Fewer resources to manage

---

## Files in This Folder

- `README.md` - This file
- `CLI-GUIDE.md` - CLI-based setup and migration
- `CONSOLE-GUIDE.md` - Console-based setup and migration
- `iam-policy.json` - IAM policy (allows S3 bucket creation)
- `agent_config.py` - Agent configuration
- `setup_infrastructure.sh` - One-time ECR setup
- `deploy_agent.py` - Deploy agent with new S3 bucket
- `verify_permissions.py` - Verify IAM permissions
- `test_agent.py` - Test deployed agent
- `cleanup.py` - Cleanup agent and its S3 bucket

---

## Quick Start

### For Infrastructure Team (One-Time)

```bash
cd new-s3-existing-ecr
./setup_infrastructure.sh
```

This creates:
- ECR repository: `bedrock-agents`
- IAM role: `BedrockAgentExecutionRole`
- IAM policy: `BedrockAgentPolicy` (allows S3 bucket creation)

### For Developers (Per Agent)

```bash
cd new-s3-existing-ecr
python3 verify_permissions.py
python3 deploy_agent.py
python3 test_agent.py
```

This creates:
- New S3 bucket: `sports-video-analyzer-data-YOUR_ACCOUNT_ID`
- Bedrock agent using the new bucket
- Agent uses shared ECR repository

---

## Comparison with Parent Folder

| Feature | Parent (Shared S3) | This Folder (New S3) |
|---------|-------------------|---------------------|
| ECR Repository | ✅ Shared | ✅ Shared |
| S3 Bucket | ✅ Shared | ❌ New per agent |
| Can Create S3 | ❌ Denied | ✅ Allowed |
| Can Create ECR | ❌ Denied | ❌ Denied |
| Data Isolation | Prefix-based | Bucket-level |
| Cost | Lower | Higher |

---

## Documentation

- **[CLI Guide](CLI-GUIDE.md)** - Complete CLI-based setup and migration
- **[Console Guide](CONSOLE-GUIDE.md)** - Complete console-based setup and migration

---

## Support

For questions about which approach to use:
- **Shared S3**: See parent folder documentation
- **New S3 per agent**: See this folder documentation

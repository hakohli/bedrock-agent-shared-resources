# Migration Guide: AWS Console Edition

**Migrate existing Bedrock agents to use shared ECR & S3 resources via AWS Console**

---

## Overview

This guide shows how to configure existing agents to use shared infrastructure using the AWS Console instead of CLI/scripts.

**Time Required**: 15 minutes  
**Downtime**: None

---

## Prerequisites

✅ Existing ECR repository: `bedrock-agents`  
✅ Existing S3 bucket: `company-bedrock-agents`  
✅ IAM role: `BedrockAgentExecutionRole`  
✅ IAM policy: `BedrockAgentDeveloperPolicy` attached to your user

---

## Part 1: Infrastructure Setup (One-Time)

### Step 1: Create ECR Repository

1. Go to **Amazon ECR Console**: https://console.aws.amazon.com/ecr/
2. Click **Create repository**
3. Configure:
   - **Repository name**: `bedrock-agents`
   - **Tag immutability**: Disabled
   - **Scan on push**: Enabled
   - **Encryption**: AES-256
4. Click **Add tag**:
   - **Key**: `auto-delete`
   - **Value**: `no`
5. Click **Create repository**

### Step 2: Create S3 Bucket

1. Go to **Amazon S3 Console**: https://console.aws.amazon.com/s3/
2. Click **Create bucket**
3. Configure:
   - **Bucket name**: `company-bedrock-agents`
   - **Region**: us-east-1 (or your preferred region)
   - **Block all public access**: Enabled
   - **Bucket Versioning**: Enabled
   - **Default encryption**: SSE-S3
4. Click **Add tag**:
   - **Key**: `auto-delete`
   - **Value**: `no`
5. Click **Create bucket**
6. Create folder structure:
   - Click into the bucket
   - Click **Create folder** → `agents/`
   - Click **Create folder** → `agents/sports-video-analyzer/`
   - Click **Create folder** → `agents/sports-video-analyzer/videos/`
   - Click **Create folder** → `agents/sports-video-analyzer/artifacts/`

### Step 3: Create IAM Execution Role

1. Go to **IAM Console**: https://console.aws.amazon.com/iam/
2. Click **Roles** → **Create role**
3. **Trusted entity type**: AWS service
4. **Use case**: Select **Bedrock** from the dropdown
5. Click **Next**
6. **Add permissions**:
   - Search and select: `AmazonBedrockFullAccess`
7. Click **Next**
8. **Role name**: `BedrockAgentExecutionRole`
9. **Add tags**:
   - **Key**: `auto-delete`, **Value**: `no`
10. Click **Create role**
11. Click on the created role
12. Click **Add permissions** → **Create inline policy**
13. Switch to **JSON** tab and paste:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
    }
  ]
}
```
14. **Policy name**: `S3Access`
15. Click **Create policy**

### Step 4: Create IAM Developer Policy

1. In **IAM Console**, click **Policies** → **Create policy**
2. Switch to **JSON** tab
3. Paste the content from `iam-policy.json` (replace `YOUR_ACCOUNT_ID` with your actual account ID)
4. Click **Next**
5. **Policy name**: `BedrockAgentDeveloperPolicy`
6. **Add tags**:
   - **Key**: `auto-delete`, **Value**: `no`
7. Click **Create policy**

### Step 5: Attach Policy to Users/Groups

1. In **IAM Console**, click **Users** or **User groups**
2. Select your user/group
3. Click **Add permissions** → **Attach policies directly**
4. Search for: `BedrockAgentDeveloperPolicy`
5. Select it and click **Add permissions**

---

## Part 2: Create New Agent Using Shared Resources

### Step 1: Navigate to Bedrock Agents

1. Go to **Amazon Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. In the left menu, click **Agents**
3. Click **Create Agent**

### Step 2: Configure Agent Details

1. **Agent details**:
   - **Agent name**: `sports-video-analyzer` (or your agent name)
   - **Description**: `Analyzes sports videos to extract game insights`
   - **User input**: Enable
2. Click **Next**

### Step 3: Configure Agent Instructions

1. **Agent instructions**:
```
You are a sports video analysis assistant. You help users analyze sports game footage to extract:
- Scoreboard information (teams, scores, time/period, game state)
- Player identification (jersey numbers, positions, names)
- Key plays (goals, assists, shots, passes, defensive actions, scoring plays)
- Game statistics and highlights
You can analyze videos from various sports including soccer, basketball, football, hockey, and more.
Provide detailed, structured analysis of sports videos.
```
2. Click **Next**

### Step 4: Select Foundation Model

1. **Select model**: `Anthropic Claude 3 Sonnet`
2. Click **Next**

### Step 5: Configure IAM Role

1. **Service role**: Select **Use an existing service role**
2. **Existing service role**: Select `BedrockAgentExecutionRole`
3. Click **Next**

### Step 6: Add Action Groups (Optional)

1. Skip for now or add Lambda-based action groups
2. Click **Next**

### Step 7: Add Knowledge Bases (Optional)

1. Skip for now or connect to existing knowledge bases
2. Click **Next**

### Step 8: Review and Create

1. Review all settings
2. Click **Create Agent**
3. Wait for agent to be created (30-60 seconds)

### Step 9: Prepare Agent

1. After creation, click **Prepare** button at the top
2. Wait for preparation to complete (~30 seconds)
3. Status will change to **Prepared**

### Step 10: Create Alias

1. In the agent details page, click **Aliases** tab
2. Click **Create alias**
3. **Alias name**: `production`
4. **Description**: `Production alias`
5. Click **Create alias**

### Step 11: Add Tags

1. In the agent details page, click **Tags** tab
2. Click **Manage tags**
3. Click **Add new tag**:
   - **Key**: `auto-delete`
   - **Value**: `no`
4. Click **Save changes**

---

## Part 3: Update Existing Agent

### Option A: Update Agent Configuration

1. Go to **Bedrock Console** → **Agents**
2. Click on your existing agent
3. Click **Edit** in Agent details section
4. Update **Agent resource role** to: `BedrockAgentExecutionRole`
5. Click **Save**
6. Click **Prepare** to apply changes

### Option B: Migrate to New Agent

1. Create new agent following Part 2 steps
2. Test new agent thoroughly
3. Update applications to use new agent ID
4. Delete old agent once migration is verified

---

## Part 4: Upload Videos to Shared S3

### Step 1: Navigate to S3 Bucket

1. Go to **S3 Console**: https://console.aws.amazon.com/s3/
2. Click on bucket: `company-bedrock-agents`
3. Navigate to: `agents/sports-video-analyzer/videos/`

### Step 2: Upload Video Files

1. Click **Upload**
2. Click **Add files** and select your video files
3. Click **Upload**
4. Note the S3 URI: `s3://company-bedrock-agents/agents/sports-video-analyzer/videos/your-video.mp4`

---

## Part 5: Test Agent

### Step 1: Test in Console

1. Go to **Bedrock Console** → **Agents**
2. Click on your agent
3. Click **Test** button in the top right
4. In the test panel, enter:
```
Analyze this sports video: s3://company-bedrock-agents/agents/sports-video-analyzer/videos/your-video.mp4
```
5. Review the response

### Step 2: Test with API

Use the AWS CLI or SDK:
```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-alias-id YOUR_ALIAS_ID \
  --session-id test-session-123 \
  --input-text "What information can you extract from sports videos?" \
  --region us-east-1
```

---

## Part 6: Monitor and Manage

### View Agent Metrics

1. Go to **Bedrock Console** → **Agents**
2. Click on your agent
3. Click **Monitoring** tab
4. View:
   - Invocation count
   - Error rate
   - Latency metrics

### View CloudWatch Logs

1. Go to **CloudWatch Console**: https://console.aws.amazon.com/cloudwatch/
2. Click **Log groups**
3. Find log group: `/aws/bedrock/agents/YOUR_AGENT_ID`
4. Click to view logs

### Update Agent

1. Go to **Bedrock Console** → **Agents**
2. Click on your agent
3. Click **Edit** in any section
4. Make changes
5. Click **Save**
6. Click **Prepare** to apply changes

---

## Verification Checklist

Use the console to verify:

- [ ] **ECR Repository exists**
  - Go to ECR Console → Check `bedrock-agents` exists
  
- [ ] **S3 Bucket exists with folders**
  - Go to S3 Console → Check `company-bedrock-agents` exists
  - Verify folder structure: `agents/sports-video-analyzer/videos/`
  
- [ ] **IAM Role configured**
  - Go to IAM Console → Roles → Check `BedrockAgentExecutionRole`
  - Verify trust policy allows bedrock.amazonaws.com
  - Verify S3 permissions attached
  
- [ ] **IAM Policy created**
  - Go to IAM Console → Policies → Check `BedrockAgentDeveloperPolicy`
  - Verify policy attached to your user/group
  
- [ ] **Agent created and prepared**
  - Go to Bedrock Console → Agents → Check your agent
  - Status should be "Prepared"
  
- [ ] **Agent uses correct role**
  - In agent details, verify Service role is `BedrockAgentExecutionRole`
  
- [ ] **Tags applied**
  - Check Tags tab shows `auto-delete: no`
  
- [ ] **Alias created**
  - Check Aliases tab shows `production` alias

---

## Troubleshooting

### Issue: Cannot create agent

**Check**:
1. Go to IAM Console → Check if `BedrockAgentDeveloperPolicy` is attached to your user
2. Go to Bedrock Console → Settings → Model access → Verify Claude 3 Sonnet is enabled

**Solution**: Request model access or attach correct policy

### Issue: Agent cannot access S3

**Check**:
1. Go to IAM Console → Roles → `BedrockAgentExecutionRole`
2. Click **Permissions** tab
3. Verify S3Access inline policy exists

**Solution**: Add S3 permissions to the role (see Step 3 above)

### Issue: Cannot see agent in console

**Check**:
1. Verify you're in the correct AWS region (top-right dropdown)
2. Go to Bedrock Console → Agents → Check region selector

**Solution**: Switch to the region where agent was created

### Issue: Test fails with "Access Denied"

**Check**:
1. Go to agent details → Service role
2. Verify it's set to `BedrockAgentExecutionRole`

**Solution**: Edit agent and update service role

---

## Console URLs Quick Reference

| Service | Console URL |
|---------|-------------|
| Bedrock Agents | https://console.aws.amazon.com/bedrock/home#/agents |
| S3 Buckets | https://console.aws.amazon.com/s3/ |
| ECR Repositories | https://console.aws.amazon.com/ecr/ |
| IAM Roles | https://console.aws.amazon.com/iam/home#/roles |
| IAM Policies | https://console.aws.amazon.com/iam/home#/policies |
| CloudWatch Logs | https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups |

---

## Best Practices

1. **Use Aliases**: Always create aliases for production deployments
2. **Tag Everything**: Apply `auto-delete: no` tag to all resources
3. **Test First**: Use the console test feature before deploying
4. **Monitor Logs**: Enable CloudWatch logging for debugging
5. **Version Control**: Document agent configuration changes
6. **Least Privilege**: Only grant necessary permissions

---

## Next Steps

1. ✅ Create additional agents using same infrastructure
2. ✅ Set up CloudWatch alarms for monitoring
3. ✅ Configure Lambda action groups for custom functionality
4. ✅ Add knowledge bases for RAG capabilities
5. ✅ Implement CI/CD for agent updates

---

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/bedrock/
- **Bedrock Agents Guide**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- **Console Help**: Click the "?" icon in any AWS Console page

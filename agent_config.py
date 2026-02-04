import os

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = 'YOUR_ACCOUNT_ID'

# Pre-approved Resources (managed by infrastructure team)
APPROVED_ECR_REPO = os.environ.get('APPROVED_ECR_REPO', 'bedrock-agents')
SHARED_S3_BUCKET = os.environ.get('SHARED_S3_BUCKET', 'company-bedrock-agents')

# IAM Role (created by infrastructure team)
AGENT_EXECUTION_ROLE = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/BedrockAgentExecutionRole"

# Agent Configuration
AGENT_CONFIG = {
    'agent_name': 'sports-video-analyzer',
    'description': 'Analyzes sports videos to extract game insights',
    'instruction': '''You are a sports video analysis assistant. You help users analyze sports game footage to extract:
- Scoreboard information (teams, scores, time/period, game state)
- Player identification (jersey numbers, positions, names)
- Key plays (goals, assists, shots, passes, defensive actions, scoring plays)
- Game statistics and highlights
You can analyze videos from various sports including soccer, basketball, football, hockey, and more.
Provide detailed, structured analysis of sports videos.''',
    'foundation_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'idle_session_ttl': 600
}

# S3 Paths within shared bucket
S3_AGENT_PREFIX = f's3://{SHARED_S3_BUCKET}/agents/{AGENT_CONFIG["agent_name"]}'
S3_ARTIFACTS_PATH = f'{S3_AGENT_PREFIX}/artifacts'
S3_VIDEOS_PATH = f'{S3_AGENT_PREFIX}/videos'

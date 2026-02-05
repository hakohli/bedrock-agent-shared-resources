import os

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID', 'YOUR_ACCOUNT_ID')

# Shared Resources
APPROVED_ECR_REPO = 'bedrock-agents'
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

# S3 Bucket - New bucket per agent
S3_BUCKET_NAME = f"{AGENT_CONFIG['agent_name']}-data-{AWS_ACCOUNT_ID}"
S3_VIDEOS_PATH = f's3://{S3_BUCKET_NAME}/videos'
S3_ARTIFACTS_PATH = f's3://{S3_BUCKET_NAME}/artifacts'

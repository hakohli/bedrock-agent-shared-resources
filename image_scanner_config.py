import os

# AWS Configuration
AWS_REGION = 'us-east-1'
AWS_ACCOUNT_ID = '395102750341'

# Existing Shared Resources
SHARED_S3_BUCKET = 'company-bedrock-agents'
APPROVED_ECR_REPO = 'bedrock-agents'
AGENT_EXECUTION_ROLE = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/BedrockAgentExecutionRole"

# Agent Configuration
AGENT_CONFIG = {
    'agent_name': 'image-scanner-agent',
    'description': 'Scans images and outputs analysis to JSON format',
    'instruction': '''You are an image analysis assistant. When given an image, you:
1. Analyze the image content (objects, people, text, scenes, colors)
2. Extract any visible text (OCR)
3. Identify key elements and their locations
4. Output the analysis in structured JSON format with these fields:
   - objects: list of detected objects
   - text: any text found in the image
   - scene: description of the overall scene
   - colors: dominant colors
   - metadata: image properties
Provide detailed, accurate analysis in valid JSON format.''',
    'foundation_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'idle_session_ttl': 600
}

# S3 Paths within shared bucket
S3_AGENT_PREFIX = f's3://{SHARED_S3_BUCKET}/agents/{AGENT_CONFIG["agent_name"]}'
S3_IMAGES_PATH = f'{S3_AGENT_PREFIX}/images'
S3_OUTPUT_PATH = f'{S3_AGENT_PREFIX}/output'

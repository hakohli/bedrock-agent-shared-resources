#!/usr/bin/env python3
"""
Deploy Bedrock Agent with new S3 bucket and existing ECR.
"""

import boto3
import json
from agent_config import (
    AWS_REGION,
    AWS_ACCOUNT_ID,
    AGENT_CONFIG,
    AGENT_EXECUTION_ROLE,
    S3_BUCKET_NAME
)

def create_s3_bucket():
    """Create new S3 bucket for the agent."""
    s3 = boto3.client('s3', region_name=AWS_REGION)
    
    print(f"Creating S3 bucket: {S3_BUCKET_NAME}")
    
    try:
        if AWS_REGION == 'us-east-1':
            s3.create_bucket(Bucket=S3_BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
        
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=S3_BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Enable encryption
        s3.put_bucket_encryption(
            Bucket=S3_BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
            }
        )
        
        # Add tags
        s3.put_bucket_tagging(
            Bucket=S3_BUCKET_NAME,
            Tagging={'TagSet': [{'Key': 'auto-delete', 'Value': 'no'}]}
        )
        
        # Create folders
        s3.put_object(Bucket=S3_BUCKET_NAME, Key='videos/')
        s3.put_object(Bucket=S3_BUCKET_NAME, Key='artifacts/')
        
        print(f"✓ S3 bucket created: {S3_BUCKET_NAME}")
        return True
        
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"✓ S3 bucket already exists: {S3_BUCKET_NAME}")
        return True
    except Exception as e:
        print(f"✗ Error creating S3 bucket: {e}")
        return False

def create_agent():
    """Create Bedrock agent."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"\nCreating agent: {AGENT_CONFIG['agent_name']}")
    
    try:
        response = bedrock.create_agent(
            agentName=AGENT_CONFIG['agent_name'],
            agentResourceRoleArn=AGENT_EXECUTION_ROLE,
            description=AGENT_CONFIG['description'],
            foundationModel=AGENT_CONFIG['foundation_model'],
            instruction=AGENT_CONFIG['instruction'],
            idleSessionTTLInSeconds=AGENT_CONFIG['idle_session_ttl'],
            tags={'auto-delete': 'no'}
        )
        
        agent_id = response['agent']['agentId']
        print(f"✓ Agent created: {agent_id}")
        return agent_id
        
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        return None

def prepare_agent(agent_id):
    """Prepare the agent."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"\nPreparing agent...")
    try:
        bedrock.prepare_agent(agentId=agent_id)
        print(f"✓ Agent prepared")
        return True
    except Exception as e:
        print(f"✗ Error preparing agent: {e}")
        return False

def create_alias(agent_id):
    """Create agent alias."""
    import time
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"\nCreating alias...")
    time.sleep(15)  # Wait for preparation
    
    try:
        response = bedrock.create_agent_alias(
            agentId=agent_id,
            agentAliasName='production'
        )
        alias_id = response['agentAlias']['agentAliasId']
        print(f"✓ Alias created: {alias_id}")
        return alias_id
    except Exception as e:
        print(f"✗ Error creating alias: {e}")
        return None

def save_deployment_info(agent_id, alias_id):
    """Save deployment information."""
    info = {
        'agent_id': agent_id,
        'alias_id': alias_id,
        'agent_name': AGENT_CONFIG['agent_name'],
        'region': AWS_REGION,
        'account_id': AWS_ACCOUNT_ID,
        's3_bucket': S3_BUCKET_NAME
    }
    
    with open('deployment_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n✓ Deployment info saved to deployment_info.json")

def main():
    print("=" * 60)
    print("Bedrock Agent Deployment - New S3 + Existing ECR")
    print("=" * 60)
    
    # Create S3 bucket
    if not create_s3_bucket():
        return
    
    # Create agent
    agent_id = create_agent()
    if not agent_id:
        return
    
    # Prepare agent
    if not prepare_agent(agent_id):
        return
    
    # Create alias
    alias_id = create_alias(agent_id)
    if not alias_id:
        return
    
    # Save deployment info
    save_deployment_info(agent_id, alias_id)
    
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print("=" * 60)
    print(f"\nAgent ID: {agent_id}")
    print(f"Alias ID: {alias_id}")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"\nNext steps:")
    print(f"1. Test: python3 test_agent.py")
    print(f"2. Upload videos: aws s3 cp video.mp4 s3://{S3_BUCKET_NAME}/videos/")

if __name__ == '__main__':
    main()

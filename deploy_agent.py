#!/usr/bin/env python3
"""
Deploy Bedrock Agent using existing ECR and S3 resources.
This script demonstrates how developers can deploy agents without creating new infrastructure.
"""

import boto3
import json
from agent_config import (
    AWS_REGION,
    AWS_ACCOUNT_ID,
    AGENT_CONFIG,
    AGENT_EXECUTION_ROLE,
    SHARED_S3_BUCKET
)

def create_agent():
    """Create a Bedrock agent using existing resources."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"Creating agent: {AGENT_CONFIG['agent_name']}")
    print(f"Using execution role: {AGENT_EXECUTION_ROLE}")
    print(f"Using S3 bucket: {SHARED_S3_BUCKET}")
    
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
        print(f"\n✓ Agent created successfully!")
        print(f"  Agent ID: {agent_id}")
        print(f"  Agent ARN: {response['agent']['agentArn']}")
        
        return agent_id
        
    except Exception as e:
        print(f"\n✗ Error creating agent: {e}")
        return None

def prepare_agent(agent_id):
    """Prepare the agent for use."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"\nPreparing agent {agent_id}...")
    
    try:
        response = bedrock.prepare_agent(agentId=agent_id)
        print(f"✓ Agent prepared successfully!")
        print(f"  Status: {response['agentStatus']}")
        return True
    except Exception as e:
        print(f"✗ Error preparing agent: {e}")
        return False

def create_agent_alias(agent_id):
    """Create an alias for the agent."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"\nCreating agent alias...")
    
    try:
        response = bedrock.create_agent_alias(
            agentId=agent_id,
            agentAliasName='production'
        )
        
        alias_id = response['agentAlias']['agentAliasId']
        print(f"✓ Agent alias created successfully!")
        print(f"  Alias ID: {alias_id}")
        return alias_id
        
    except Exception as e:
        print(f"✗ Error creating alias: {e}")
        return None

def save_deployment_info(agent_id, alias_id):
    """Save deployment information for later use."""
    deployment_info = {
        'agent_id': agent_id,
        'alias_id': alias_id,
        'agent_name': AGENT_CONFIG['agent_name'],
        'region': AWS_REGION,
        'account_id': AWS_ACCOUNT_ID,
        's3_bucket': SHARED_S3_BUCKET
    }
    
    with open('deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n✓ Deployment info saved to deployment_info.json")

def main():
    print("=" * 60)
    print("Bedrock Agent Deployment Demo")
    print("Using Existing ECR and S3 Resources")
    print("=" * 60)
    
    # Create agent
    agent_id = create_agent()
    if not agent_id:
        return
    
    # Prepare agent
    if not prepare_agent(agent_id):
        return
    
    # Create alias
    alias_id = create_agent_alias(agent_id)
    if not alias_id:
        return
    
    # Save deployment info
    save_deployment_info(agent_id, alias_id)
    
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Test the agent: python test_agent.py")
    print(f"2. View in console: https://console.aws.amazon.com/bedrock/home?region={AWS_REGION}#/agents/{agent_id}")

if __name__ == '__main__':
    main()

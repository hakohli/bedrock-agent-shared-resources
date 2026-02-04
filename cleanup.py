#!/usr/bin/env python3
"""
Clean up deployed agent resources.
"""

import boto3
import json
from agent_config import AWS_REGION

def load_deployment_info():
    """Load deployment information."""
    try:
        with open('deployment_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("No deployment_info.json found. Nothing to clean up.")
        return None

def delete_agent(agent_id):
    """Delete the Bedrock agent."""
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    print(f"Deleting agent: {agent_id}")
    
    try:
        bedrock.delete_agent(agentId=agent_id, skipResourceInUseCheck=True)
        print("✓ Agent deleted successfully")
        return True
    except Exception as e:
        print(f"✗ Error deleting agent: {e}")
        return False

def main():
    print("=" * 60)
    print("Cleanup Deployed Agent")
    print("=" * 60)
    
    info = load_deployment_info()
    if not info:
        return
    
    print(f"\nAgent ID: {info['agent_id']}")
    print(f"Agent Name: {info['agent_name']}")
    
    confirm = input("\nAre you sure you want to delete this agent? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    if delete_agent(info['agent_id']):
        print("\n✓ Cleanup complete!")
        print("\nNote: Shared infrastructure (ECR, S3, IAM) was not deleted.")
        print("Contact infrastructure team if those resources need cleanup.")

if __name__ == '__main__':
    main()

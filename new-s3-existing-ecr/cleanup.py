#!/usr/bin/env python3
"""
Clean up agent and its S3 bucket.
"""

import boto3
import json

def load_deployment_info():
    try:
        with open('deployment_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("No deployment_info.json found.")
        return None

def delete_agent(agent_id, region):
    bedrock = boto3.client('bedrock-agent', region_name=region)
    print(f"Deleting agent: {agent_id}")
    try:
        bedrock.delete_agent(agentId=agent_id, skipResourceInUseCheck=True)
        print("✓ Agent deleted")
        return True
    except Exception as e:
        print(f"✗ Error deleting agent: {e}")
        return False

def delete_s3_bucket(bucket_name, region):
    s3 = boto3.client('s3', region_name=region)
    print(f"\nEmptying and deleting S3 bucket: {bucket_name}")
    try:
        # Empty bucket
        paginator = s3.get_paginator('list_object_versions')
        for page in paginator.paginate(Bucket=bucket_name):
            objects = []
            if 'Versions' in page:
                objects.extend([{'Key': v['Key'], 'VersionId': v['VersionId']} for v in page['Versions']])
            if 'DeleteMarkers' in page:
                objects.extend([{'Key': d['Key'], 'VersionId': d['VersionId']} for d in page['DeleteMarkers']])
            
            if objects:
                s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
        
        # Delete bucket
        s3.delete_bucket(Bucket=bucket_name)
        print("✓ S3 bucket deleted")
        return True
    except Exception as e:
        print(f"✗ Error deleting S3 bucket: {e}")
        return False

def main():
    print("=" * 60)
    print("Cleanup Agent and S3 Bucket")
    print("=" * 60)
    
    info = load_deployment_info()
    if not info:
        return
    
    print(f"\nAgent ID: {info['agent_id']}")
    print(f"S3 Bucket: {info['s3_bucket']}")
    
    confirm = input("\nDelete agent and S3 bucket? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    delete_agent(info['agent_id'], info['region'])
    delete_s3_bucket(info['s3_bucket'], info['region'])
    
    print("\n✓ Cleanup complete!")
    print("\nNote: Shared ECR repository was not deleted.")

if __name__ == '__main__':
    main()

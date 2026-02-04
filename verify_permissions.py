#!/usr/bin/env python3
"""
Verify IAM permissions before deploying agent.
This helps developers confirm they have the right permissions.
"""

import boto3
import json
from agent_config import AWS_REGION, AWS_ACCOUNT_ID, SHARED_S3_BUCKET, APPROVED_ECR_REPO

def check_bedrock_permissions():
    """Check if user can perform Bedrock operations."""
    print("\n1. Checking Bedrock permissions...")
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    
    try:
        bedrock.list_agents(maxResults=1)
        print("   ✓ Can list agents")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access Bedrock: {e}")
        return False

def check_s3_permissions():
    """Check if user can access the shared S3 bucket."""
    print("\n2. Checking S3 permissions...")
    s3 = boto3.client('s3', region_name=AWS_REGION)
    
    try:
        s3.head_bucket(Bucket=SHARED_S3_BUCKET)
        print(f"   ✓ Can access bucket: {SHARED_S3_BUCKET}")
        
        # Try to list objects
        s3.list_objects_v2(Bucket=SHARED_S3_BUCKET, MaxKeys=1)
        print(f"   ✓ Can list objects in bucket")
        
        return True
    except Exception as e:
        print(f"   ✗ Cannot access S3 bucket: {e}")
        return False

def check_ecr_permissions():
    """Check if user can access the ECR repository."""
    print("\n3. Checking ECR permissions...")
    ecr = boto3.client('ecr', region_name=AWS_REGION)
    
    try:
        ecr.describe_repositories(repositoryNames=[APPROVED_ECR_REPO])
        print(f"   ✓ Can access ECR repository: {APPROVED_ECR_REPO}")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access ECR repository: {e}")
        return False

def check_iam_permissions():
    """Check if user can pass the execution role."""
    print("\n4. Checking IAM permissions...")
    iam = boto3.client('iam', region_name=AWS_REGION)
    
    try:
        iam.get_role(RoleName='BedrockAgentExecutionRole')
        print(f"   ✓ Can access BedrockAgentExecutionRole")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access IAM role: {e}")
        return False

def check_denied_operations():
    """Verify that resource creation is denied."""
    print("\n5. Checking denied operations (should fail)...")
    
    # Try to create S3 bucket (should be denied)
    s3 = boto3.client('s3', region_name=AWS_REGION)
    try:
        s3.create_bucket(Bucket='test-should-fail-bucket')
        print("   ✗ WARNING: Can create S3 buckets (should be denied)")
        return False
    except Exception as e:
        if 'AccessDenied' in str(e) or 'Denied' in str(e):
            print("   ✓ S3 bucket creation correctly denied")
        else:
            print(f"   ? Unexpected error: {e}")
    
    # Try to create ECR repository (should be denied)
    ecr = boto3.client('ecr', region_name=AWS_REGION)
    try:
        ecr.create_repository(repositoryName='test-should-fail-repo')
        print("   ✗ WARNING: Can create ECR repositories (should be denied)")
        return False
    except Exception as e:
        if 'AccessDenied' in str(e) or 'Denied' in str(e):
            print("   ✓ ECR repository creation correctly denied")
        else:
            print(f"   ? Unexpected error: {e}")
    
    return True

def main():
    print("=" * 60)
    print("IAM Permissions Verification")
    print("=" * 60)
    print(f"Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {AWS_REGION}")
    
    results = {
        'bedrock': check_bedrock_permissions(),
        's3': check_s3_permissions(),
        'ecr': check_ecr_permissions(),
        'iam': check_iam_permissions(),
        'denied': check_denied_operations()
    }
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check.upper()}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All checks passed! Ready to deploy agents.")
        print("\nRun: python deploy_agent.py")
    else:
        print("✗ Some checks failed. Contact your infrastructure team.")
        print("\nRequired policy: BedrockAgentDeveloperPolicy")
    print("=" * 60)

if __name__ == '__main__':
    main()

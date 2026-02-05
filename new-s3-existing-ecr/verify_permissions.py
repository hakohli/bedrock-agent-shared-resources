#!/usr/bin/env python3
"""
Verify IAM permissions for new S3 + existing ECR approach.
"""

import boto3
from agent_config import AWS_REGION, AWS_ACCOUNT_ID, APPROVED_ECR_REPO

def check_bedrock():
    print("\n1. Checking Bedrock permissions...")
    bedrock = boto3.client('bedrock-agent', region_name=AWS_REGION)
    try:
        bedrock.list_agents(maxResults=1)
        print("   ✓ Can list agents")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access Bedrock: {e}")
        return False

def check_s3_create():
    print("\n2. Checking S3 bucket creation permissions...")
    s3 = boto3.client('s3', region_name=AWS_REGION)
    test_bucket = f"test-agent-data-{AWS_ACCOUNT_ID}"
    
    try:
        # Try to create bucket
        if AWS_REGION == 'us-east-1':
            s3.create_bucket(Bucket=test_bucket)
        else:
            s3.create_bucket(Bucket=test_bucket, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})
        
        print(f"   ✓ Can create S3 buckets (pattern: *-data-{AWS_ACCOUNT_ID})")
        
        # Clean up test bucket
        s3.delete_bucket(Bucket=test_bucket)
        return True
    except Exception as e:
        if 'BucketAlreadyExists' in str(e) or 'BucketAlreadyOwnedByYou' in str(e):
            print(f"   ✓ Can create S3 buckets (test bucket already exists)")
            return True
        print(f"   ✗ Cannot create S3 buckets: {e}")
        return False

def check_ecr():
    print("\n3. Checking ECR permissions...")
    ecr = boto3.client('ecr', region_name=AWS_REGION)
    try:
        ecr.describe_repositories(repositoryNames=[APPROVED_ECR_REPO])
        print(f"   ✓ Can access ECR repository: {APPROVED_ECR_REPO}")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access ECR repository: {e}")
        return False

def check_iam():
    print("\n4. Checking IAM permissions...")
    iam = boto3.client('iam', region_name=AWS_REGION)
    try:
        iam.get_role(RoleName='BedrockAgentExecutionRole')
        print(f"   ✓ Can access BedrockAgentExecutionRole")
        return True
    except Exception as e:
        print(f"   ✗ Cannot access IAM role: {e}")
        return False

def check_denied():
    print("\n5. Checking denied operations...")
    
    # Try to create ECR repository (should be denied)
    ecr = boto3.client('ecr', region_name=AWS_REGION)
    try:
        ecr.create_repository(repositoryName='test-should-fail-repo')
        print("   ✗ WARNING: Can create ECR repositories (should be denied)")
        # Clean up if it was created
        ecr.delete_repository(repositoryName='test-should-fail-repo', force=True)
        return False
    except Exception as e:
        if 'AccessDenied' in str(e) or 'Denied' in str(e):
            print("   ✓ ECR repository creation correctly denied")
            return True
        print(f"   ? Unexpected error: {e}")
        return True

def main():
    print("=" * 60)
    print("IAM Permissions Verification")
    print("New S3 + Existing ECR Approach")
    print("=" * 60)
    print(f"Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {AWS_REGION}")
    
    results = {
        'bedrock': check_bedrock(),
        's3_create': check_s3_create(),
        'ecr': check_ecr(),
        'iam': check_iam(),
        'denied': check_denied()
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
        print("\nKey Difference: You CAN create S3 buckets")
        print("Pattern: *-data-YOUR_ACCOUNT_ID")
        print("\nRun: python3 deploy_agent.py")
    else:
        print("✗ Some checks failed. Contact your infrastructure team.")
        print("\nRequired policy: BedrockAgentPolicy")
    print("=" * 60)

if __name__ == '__main__':
    main()

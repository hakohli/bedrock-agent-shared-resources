#!/usr/bin/env python3
"""
Test the deployed Bedrock agent.
"""

import boto3
import json
import time

def load_deployment_info():
    """Load deployment information."""
    try:
        with open('deployment_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: deployment_info.json not found. Run deploy_agent.py first.")
        return None

def invoke_agent(agent_id, alias_id, prompt):
    """Invoke the Bedrock agent with a prompt."""
    bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    print(f"\nInvoking agent with prompt: {prompt}")
    print("-" * 60)
    
    try:
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=f"test-session-{int(time.time())}",
            inputText=prompt
        )
        
        # Process streaming response
        event_stream = response['completion']
        full_response = ""
        
        for event in event_stream:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
                    print(text, end='', flush=True)
        
        print("\n" + "-" * 60)
        return full_response
        
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None

def main():
    print("=" * 60)
    print("Bedrock Agent Test")
    print("=" * 60)
    
    # Load deployment info
    info = load_deployment_info()
    if not info:
        return
    
    print(f"\nAgent ID: {info['agent_id']}")
    print(f"Alias ID: {info['alias_id']}")
    print(f"Agent Name: {info['agent_name']}")
    
    # Test prompts
    test_prompts = [
        "What kind of information can you extract from baseball videos?",
        "Analyze a baseball video at s3://company-bedrock-agents/agents/baseball-video-analyzer/videos/sample.mp4",
        "What scoreboard information do you look for?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"Test {i}/{len(test_prompts)}")
        print(f"{'=' * 60}")
        
        response = invoke_agent(info['agent_id'], info['alias_id'], prompt)
        
        if i < len(test_prompts):
            print("\nWaiting 2 seconds before next test...")
            time.sleep(2)
    
    print(f"\n{'=' * 60}")
    print("Testing Complete!")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    main()

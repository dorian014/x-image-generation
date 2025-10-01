#!/usr/bin/env python3
"""
Test script to verify Vertex AI Imagen setup
"""

import subprocess
import os
import sys

def test_gcloud_auth():
    """Test if gcloud authentication is set up"""
    print("Testing gcloud authentication...")
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'],
                              capture_output=True, text=True, check=True)
        if "ACTIVE" in result.stdout:
            print("✓ gcloud authentication is active")
            return True
        else:
            print("✗ No active gcloud authentication found")
            print("  Run: gcloud auth login")
            return False
    except FileNotFoundError:
        print("✗ gcloud CLI not found")
        print("  Install from: https://cloud.google.com/sdk/docs/install")
        return False
    except Exception as e:
        print(f"✗ Error checking gcloud auth: {e}")
        return False

def test_project_id():
    """Test if project ID is set"""
    print("\nTesting Google Cloud project...")
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'],
                              capture_output=True, text=True, check=True)
        project_id = result.stdout.strip()
        if project_id:
            print(f"✓ Project ID: {project_id}")
            return project_id
        else:
            print("✗ No project ID set")
            print("  Run: gcloud config set project qstarlabs-dev")
            return None
    except Exception as e:
        print(f"✗ Error getting project ID: {e}")
        return None

def test_application_credentials():
    """Test if application default credentials are set"""
    print("\nTesting application default credentials...")
    try:
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'],
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✓ Application default credentials are set")
            return True
        else:
            print("✗ Application default credentials not set")
            print("  Run: gcloud auth application-default login")
            return False
    except Exception as e:
        print(f"✗ Error checking credentials: {e}")
        return False

def test_vertex_api():
    """Test if Vertex AI API is enabled"""
    print("\nTesting Vertex AI API...")
    try:
        result = subprocess.run(['gcloud', 'services', 'list', '--filter=aiplatform.googleapis.com'],
                              capture_output=True, text=True, check=True)
        if "aiplatform.googleapis.com" in result.stdout:
            print("✓ Vertex AI API is enabled")
            return True
        else:
            print("✗ Vertex AI API is not enabled")
            print("  Run: gcloud services enable aiplatform.googleapis.com")
            return False
    except Exception as e:
        print(f"✗ Error checking Vertex AI API: {e}")
        return False

def test_imagen_access():
    """Test basic Imagen API access"""
    print("\nTesting Imagen model access...")
    try:
        import requests
        import json

        # Get project ID
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'],
                              capture_output=True, text=True, check=True)
        project_id = result.stdout.strip()

        # Get access token
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'],
                              capture_output=True, text=True, check=True)
        access_token = result.stdout.strip()

        # Test API endpoint
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagegeneration@006:predict"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Simple test payload
        payload = {
            "instances": [{"prompt": "test"}],
            "parameters": {
                "sampleCount": 1,
                "sampleImageSize": 256  # Small size for testing
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print("✓ Successfully connected to Imagen API")
            return True
        elif response.status_code == 403:
            print("✗ Access denied to Imagen API")
            print("  Make sure Imagen is available in your project")
            return False
        elif response.status_code == 404:
            print("✗ Imagen model not found")
            print("  The model might not be available in your region")
            return False
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"✗ Error testing Imagen access: {e}")
        return False

def main():
    print("="*50)
    print("X Image Generator - Setup Test")
    print("="*50)

    tests_passed = 0
    tests_total = 5

    if test_gcloud_auth():
        tests_passed += 1

    if test_project_id():
        tests_passed += 1

    if test_application_credentials():
        tests_passed += 1

    if test_vertex_api():
        tests_passed += 1

    if test_imagen_access():
        tests_passed += 1

    print("\n" + "="*50)
    print(f"Results: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("✓ All tests passed! You're ready to generate images.")
        print("\nRun test generation: python x_image_generator.py test")
        print("Run full generation: python x_image_generator.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
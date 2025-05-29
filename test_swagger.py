#!/usr/bin/env python3
"""
Test script for Swagger documentation and API endpoints.

This script demonstrates how to test the Contoso Creative Writing Assistant API
and access the automatically generated Swagger documentation.
"""

import requests
import json
import time
from typing import Dict, Any

def test_swagger_endpoints():
    """Test the API endpoints and demonstrate Swagger functionality."""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Contoso Creative Writing Assistant API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing Health Check Endpoint")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test status endpoint
    print("\n2. Testing API Status Endpoint")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test agents endpoint
    print("\n3. Testing Agents Information Endpoint")
    try:
        response = requests.get(f"{base_url}/api/agents")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Swagger Documentation URLs
    print("\n4. Swagger Documentation URLs")
    print(f"📚 Interactive Swagger UI: {base_url}/docs")
    print(f"📄 ReDoc Documentation: {base_url}/redoc")
    print(f"🔧 OpenAPI JSON Schema: {base_url}/openapi.json")
    
    # Example article creation request
    print("\n5. Example Article Creation Request")
    sample_task = {
        "research": "Can you find the latest camping trends and what folks are doing in the winter?",
        "products": "Can you use a selection of tents and sleeping bags as context?",
        "assignment": "Write a fun and engaging article that includes the research and product information. The article should be between 800 and 1000 words."
    }
    
    print("Sample request payload:")
    print(json.dumps(sample_task, indent=2))
    print(f"\nTo test article creation:")
    print(f"curl -X POST '{base_url}/api/article' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{json.dumps(sample_task)}'")
    
    print("\n6. Image Upload Example")
    print(f"To test image upload:")
    print(f"curl -X POST '{base_url}/api/upload-image' \\")
    print(f"  -F 'file=@your-image.jpg'")

def main():
    """Main function to run tests and display information."""
    
    print("Contoso Creative Writing Assistant - Swagger Documentation Test")
    print("============================================================")
    
    print("\n🌟 Swagger Features Added:")
    print("• Comprehensive API documentation with descriptions")
    print("• Request/response models with examples")
    print("• Interactive testing interface")
    print("• Organized endpoints with tags")
    print("• Error response documentation")
    print("• Authentication and configuration info")
    
    print("\n📖 How to Access Swagger Documentation:")
    print("1. Start the FastAPI server: python main.py")
    print("2. Open your browser to: http://localhost:8000/docs")
    print("3. Explore the interactive API documentation")
    print("4. Test endpoints directly from the browser")
    
    # Run the tests
    test_swagger_endpoints()
    
    print("\n✨ Swagger documentation is now available!")
    print("Visit http://localhost:8000/docs to explore the interactive API documentation.")

if __name__ == "__main__":
    main()

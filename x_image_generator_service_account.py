"""
Alternative authentication using Service Account
More similar to how Google Apps Script works
"""

import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class XImageGeneratorServiceAccount:
    """Image generator using service account authentication"""

    def __init__(self, service_account_file='service-account.json'):
        """
        Initialize with service account credentials

        Args:
            service_account_file: Path to service account JSON file
        """
        self.project_id = "qstarlabs-dev"
        self.location = "us-central1"
        self.imagen_model = "imagegeneration@006"

        # Set up authentication with service account
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

    def get_access_token(self):
        """
        Get access token similar to ScriptApp.getOAuthToken()
        """
        # Refresh the credentials if needed
        request = Request()
        self.credentials.refresh(request)
        return self.credentials.token

    def generate_image(self, prompt, aspect_ratio="1:1"):
        """
        Generate an image using the service account token
        """
        # Get fresh token (like ScriptApp.getOAuthToken())
        access_token = self.get_access_token()

        # Prepare Vertex AI endpoint URL
        url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.imagen_model}:predict"

        # Prepare the request (same as Apps Script)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": aspect_ratio,
                "negativePrompt": "text, watermark, logo, brand",
                "addWatermark": False
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()


# To use this approach:
# 1. Create a service account in Google Cloud Console
# 2. Download the JSON key file as 'service-account.json'
# 3. Grant it Vertex AI User permissions
# 4. Use like this:

if __name__ == "__main__":
    generator = XImageGeneratorServiceAccount('service-account.json')
    result = generator.generate_image("cartoon robot face")
    print(result)
"""
X (Twitter) Image Generator using Vertex AI - V2
Using proper SDK authentication like qstarlabs-utils
"""

import os
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging
import base64

# Google Cloud imports - same as qstarlabs-utils
from google.cloud import aiplatform
from google.api_core.exceptions import ResourceExhausted

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XImageGenerator:
    """Generate cartoon-style images for X (Twitter) using Vertex AI"""

    def __init__(self, project_id: str = "qstarlabs-dev", location: str = "us-central1"):
        """
        Initialize the image generator with Vertex AI SDK
        Using the same authentication approach as qstarlabs-utils
        """
        self.project_id = project_id
        self.location = location
        self.output_dir = Path("generated_images")

        # Create output directories
        self.header_dir = self.output_dir / "headers"
        self.profile_dir = self.output_dir / "profiles"
        self.header_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        # Set up Google Cloud project (like qstarlabs-utils)
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

        # Initialize Vertex AI SDK (handles auth automatically)
        logger.info(f"Initializing Vertex AI with project: {project_id}")
        aiplatform.init(
            project=project_id,
            location=location
        )

        logger.info("Successfully initialized Vertex AI SDK")

        # Rate limiting configuration
        self.batch_size = 5
        self.delay_between_images = 3
        self.delay_between_batches = 15

        # Image generation statistics
        self.stats = {
            "headers_requested": 0,
            "headers_successful": 0,
            "profiles_requested": 0,
            "profiles_successful": 0,
            "errors": []
        }

    def generate_header_prompts(self) -> List[str]:
        """Generate diverse prompts for X header backgrounds"""
        base_prompts = [
            "vibrant cartoon landscape with rolling hills and fluffy clouds, flat design, vector art style",
            "abstract geometric patterns with circles and triangles, cartoon style, pastel colors",
            "cartoon space scene with planets and stars, retro futuristic, bright neon colors",
            "underwater cartoon scene with coral and bubbles, vibrant colors, stylized design",
            "cartoon city skyline silhouette with simple shapes, gradient sky, minimalist design",
        ]

        enhanced_prompts = []
        for prompt in base_prompts[:2]:  # Just 2 for testing
            enhanced = f"{prompt}, no text, no people, no brands, cartoon illustration, professional quality"
            enhanced_prompts.append(enhanced)

        return enhanced_prompts

    def generate_profile_prompts(self) -> List[str]:
        """Generate diverse prompts for X profile images"""
        base_prompts = [
            "cute cartoon robot face, simple design, friendly expression",
            "cartoon cat face, minimalist style, big eyes",
        ]

        enhanced_prompts = []
        for prompt in base_prompts:
            enhanced = f"{prompt}, no text, no watermarks, square format, cartoon illustration"
            enhanced_prompts.append(enhanced)

        return enhanced_prompts

    def generate_image_with_vertex(self, prompt: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
        """
        Generate a single image using Vertex AI SDK (like qstarlabs-utils)
        """
        try:
            from vertexai.preview.vision_models import ImageGenerationModel

            # Initialize the model
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")

            # Generate the image
            logger.info(f"Generating image with prompt: {prompt[:50]}...")

            # Generate image with the model
            images = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                language="en",
                aspect_ratio=aspect_ratio,
                negative_prompt="text, watermark, logo, brand, signature, low quality, blurry, realistic photo, human, person, face",
                seed=random.randint(0, 1000000)
            )

            if images:
                # Get the first image
                image = images[0]

                # Get image bytes
                image_bytes = image._image_bytes

                return {
                    "success": True,
                    "image_data": image_bytes,
                    "prompt": prompt
                }
            else:
                return {
                    "success": False,
                    "error": "No image generated",
                    "prompt": prompt
                }

        except ResourceExhausted as e:
            logger.warning(f"Rate limit hit: {e}")
            return {
                "success": False,
                "error": f"Rate limit: {str(e)}",
                "prompt": prompt
            }
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }

    def save_image(self, image_data: bytes, filename: str, image_type: str) -> bool:
        """Save image data to file"""
        try:
            if image_type == "header":
                filepath = self.header_dir / filename
            else:
                filepath = self.profile_dir / filename

            with open(filepath, 'wb') as f:
                f.write(image_data)

            logger.info(f"Saved {image_type} image: {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to save image {filename}: {e}")
            return False

    def generate_batch(self, prompts: List[str], image_type: str, start_id: int) -> List[Dict[str, Any]]:
        """Generate a batch of images"""
        results = []
        aspect_ratio = "3:1" if image_type == "header" else "1:1"

        for i, prompt in enumerate(prompts):
            image_id = start_id + i
            logger.info(f"Generating {image_type} image {image_id}...")

            # Generate the image
            result = self.generate_image_with_vertex(prompt, aspect_ratio)
            result["image_id"] = image_id
            result["image_type"] = image_type

            # Save if successful
            if result["success"] and result.get("image_data"):
                filename = f"{image_type}_{str(image_id).zfill(3)}.png"
                if self.save_image(result["image_data"], filename, image_type):
                    result["filename"] = filename
                    if image_type == "header":
                        self.stats["headers_successful"] += 1
                    else:
                        self.stats["profiles_successful"] += 1
            else:
                self.stats["errors"].append({
                    "image_id": image_id,
                    "type": image_type,
                    "error": result.get("error", "Unknown error")
                })

            results.append(result)

            # Rate limiting
            if i < len(prompts) - 1:
                time.sleep(self.delay_between_images)

        return results

    def generate_all_images(self, num_headers: int = 2, num_profiles: int = 2):
        """Generate all X images"""
        logger.info(f"Starting generation of {num_headers} headers and {num_profiles} profiles")

        self.stats["headers_requested"] = num_headers
        self.stats["profiles_requested"] = num_profiles

        all_results = []

        # Generate header prompts
        logger.info("Generating header prompts...")
        header_prompts = self.generate_header_prompts()[:num_headers]

        # Process headers
        logger.info("\n===== Generating Header Images =====")
        batch_results = self.generate_batch(header_prompts, "header", 1)
        all_results.extend(batch_results)

        # Generate profile prompts
        logger.info("\nGenerating profile prompts...")
        profile_prompts = self.generate_profile_prompts()[:num_profiles]

        # Process profiles
        logger.info("\n===== Generating Profile Images =====")
        batch_results = self.generate_batch(profile_prompts, "profile", num_headers + 1)
        all_results.extend(batch_results)

        # Generate final report
        self.generate_final_report(all_results)

        return all_results

    def generate_final_report(self, all_results: List[Dict]):
        """Generate and save final report"""
        success_rate = ((self.stats["headers_successful"] + self.stats["profiles_successful"]) /
                       (self.stats["headers_requested"] + self.stats["profiles_requested"]) * 100)

        report = {
            "summary": {
                "total_requested": self.stats["headers_requested"] + self.stats["profiles_requested"],
                "total_successful": self.stats["headers_successful"] + self.stats["profiles_successful"],
                "success_rate": f"{success_rate:.2f}%",
                "headers": {
                    "requested": self.stats["headers_requested"],
                    "successful": self.stats["headers_successful"],
                    "failed": self.stats["headers_requested"] - self.stats["headers_successful"]
                },
                "profiles": {
                    "requested": self.stats["profiles_requested"],
                    "successful": self.stats["profiles_successful"],
                    "failed": self.stats["profiles_requested"] - self.stats["profiles_successful"]
                }
            },
            "timestamp": datetime.now().isoformat(),
            "output_directory": str(self.output_dir),
            "errors": self.stats["errors"]
        }

        # Save report
        report_path = self.output_dir / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "="*50)
        print("FINAL REPORT")
        print("="*50)
        print(f"Headers: {self.stats['headers_successful']}/{self.stats['headers_requested']} successful")
        print(f"Profiles: {self.stats['profiles_successful']}/{self.stats['profiles_requested']} successful")
        print(f"Overall Success Rate: {success_rate:.2f}%")
        print(f"Images saved to: {self.output_dir}")
        print(f"Report saved to: {report_path}")
        print("="*50)


def test_generation():
    """Test with a small batch"""
    generator = XImageGenerator()

    print("Testing with 2 headers and 2 profiles...")
    results = generator.generate_all_images(num_headers=2, num_profiles=2)

    print("\nTest Results:")
    for r in results:
        status = "Success" if r.get("success") else f"Failed - {r.get('error')}"
        print(f"  {r.get('image_type')} {r.get('image_id')}: {status}")


def main():
    """Main function to generate all 300 images"""
    generator = XImageGenerator()
    results = generator.generate_all_images(num_headers=150, num_profiles=150)
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_generation()
    else:
        main()
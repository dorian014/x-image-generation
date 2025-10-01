"""
X (Twitter) Image Generator using Vertex AI
Generate header backgrounds (1500x500) and profile images (square)
"""

import os
import json
import time
import random
import subprocess
import requests
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

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
        Initialize the image generator with Vertex AI

        Args:
            project_id: Your Google Cloud project ID
            location: The region for Vertex AI (us-central1 recommended)
        """
        self.project_id = project_id
        self.location = location
        self.output_dir = Path("generated_images")

        # Create output directories
        self.header_dir = self.output_dir / "headers"
        self.profile_dir = self.output_dir / "profiles"
        self.header_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        # Set up Google Cloud project
        logger.info(f"Initializing with project: {project_id}")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

        # Model configuration
        self.imagen_model = "imagegeneration@006"  # Imagen 3 model ID

        # Rate limiting configuration
        self.batch_size = 5  # Smaller batches for Imagen
        self.delay_between_images = 3  # 3 seconds between images
        self.delay_between_batches = 15  # 15 seconds between batches

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
            "abstract waves and curves pattern, cartoon style, rainbow gradient, dynamic flow",
            "cartoon forest with stylized trees, flat design, autumn colors",
            "geometric pattern with hexagons, cartoon style, bright complementary colors",
            "cartoon clouds and rainbows, kawaii style, pastel colors, simple shapes",
            "abstract cartoon mountains with sun, minimalist design, warm colors",
            "cartoon desert landscape with cacti silhouettes, sunset colors, simple shapes",
            "retro cartoon pattern with stars and moons, vintage colors",
            "cartoon tropical leaves pattern, bright green and pink",
            "abstract cartoon bubbles floating, rainbow colors, glossy effect",
            "cartoon circuit board pattern, tech aesthetic, neon colors",
            "stylized cartoon waves, Japanese art inspired, blue gradient",
            "cartoon crystals and gems pattern, bright jewel tones, geometric",
            "abstract cartoon smoke swirls, gradient colors, dreamy effect",
            "cartoon food pattern with fruits, kawaii style, bright colors",
            "geometric cartoon pattern with dots and lines, memphis style"
        ]

        # Add style variations
        styles = ["flat design", "isometric", "minimalist", "vector art", "retro"]
        moods = ["cheerful", "energetic", "calm", "playful", "vibrant"]

        enhanced_prompts = []
        for prompt in base_prompts:
            for i in range(8):  # Create 8 variations of each base prompt
                style = random.choice(styles)
                mood = random.choice(moods)
                enhanced = f"{prompt}, {mood} mood, {style} style, no text, no people, no brands, no logos, cartoon illustration, professional quality, 1500x500 aspect ratio"
                enhanced_prompts.append(enhanced)

        return enhanced_prompts[:150]  # Return 150 header prompts

    def generate_profile_prompts(self) -> List[str]:
        """Generate diverse prompts for X profile images"""
        base_prompts = [
            "cute cartoon robot face, simple design, friendly expression",
            "cartoon cat face, minimalist style, big eyes",
            "cartoon avocado character, kawaii style, happy face",
            "abstract cartoon smiley face, unique design",
            "cartoon pizza slice character, cute style, simple features",
            "cartoon cloud with rainbow, kawaii style",
            "cartoon star character, glowing effect, happy expression",
            "cartoon cactus with flowers, cute design, simple shapes",
            "cartoon donut character, sprinkles, happy face",
            "cartoon lightning bolt, cool design, neon effect",
            "cartoon moon face, dreamy expression",
            "cartoon diamond shape, crystal effect, rainbow colors",
            "cartoon flame character, friendly fire",
            "cartoon planet with rings, cute space theme",
            "cartoon ice cream cone, kawaii style",
            "cartoon mushroom character, fantasy style",
            "cartoon heart shape, glossy effect, gradient",
            "cartoon octopus face, simple design, happy",
            "cartoon unicorn head, minimalist style, rainbow mane",
            "cartoon alien face, friendly design",
            "cartoon panda face, simple geometric shapes",
            "cartoon fox face, geometric style",
            "cartoon owl face, big eyes",
            "cartoon bear face, minimalist design",
            "cartoon bunny face, long ears",
            "cartoon penguin face, simple shapes",
            "cartoon koala face, gray colors",
            "cartoon sloth face, slow and happy",
            "cartoon llama face, fluffy design",
            "cartoon bee character, stripes and wings"
        ]

        # Add color variations
        color_schemes = ["pastel colors", "bright colors", "neon colors", "warm tones", "cool tones"]
        styles = ["flat design", "3D effect", "minimalist", "kawaii", "geometric"]

        enhanced_prompts = []
        for prompt in base_prompts:
            for i in range(5):  # Create 5 variations of each base prompt
                colors = random.choice(color_schemes)
                style = random.choice(styles)
                enhanced = f"{prompt}, {colors}, {style} style, no text, no watermarks, square format, cartoon illustration, professional quality"
                enhanced_prompts.append(enhanced)

        return enhanced_prompts[:150]  # Return 150 profile prompts

    def generate_image_with_imagen(self, prompt: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
        """
        Generate a single image using Vertex AI's Imagen model

        Args:
            prompt: The image generation prompt
            aspect_ratio: The aspect ratio ("3:1" for headers, "1:1" for profiles)

        Returns:
            Dictionary with generation results
        """
        try:
            import requests
            import json

            # Prepare Vertex AI endpoint URL
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.imagen_model}:predict"

            # Get access token
            import subprocess
            result = subprocess.run(['gcloud', 'auth', 'print-access-token'],
                                  capture_output=True, text=True, check=True)
            access_token = result.stdout.strip()

            # Set image size based on aspect ratio
            if aspect_ratio == "3:1":
                # For headers - closest to 1500x500
                image_size = "1536x512"  # Actual 3:1 aspect ratio
            else:
                # For profiles - square
                image_size = "1024x1024"

            # Prepare the request payload for Imagen
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": aspect_ratio,
                    "negativePrompt": "text, watermark, logo, brand, signature, low quality, blurry, realistic photo, human, person, face, letters, words, writing",
                    "sampleImageSize": image_size.split('x')[0],  # Use width as size hint
                    "addWatermark": False,
                    "seed": random.randint(0, 1000000)  # Random seed for variety
                }
            }

            # Make the request
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                if 'predictions' in result and len(result['predictions']) > 0:
                    # Decode base64 image
                    image_base64 = result['predictions'][0].get('bytesBase64Encoded', '')
                    if image_base64:
                        import base64
                        image_data = base64.b64decode(image_base64)
                        return {
                            "success": True,
                            "image_data": image_data,
                            "prompt": prompt
                        }

            # Handle errors
            error_msg = f"API returned {response.status_code}"
            if response.status_code == 429:
                error_msg = "Rate limit exceeded"
            elif response.status_code == 403:
                error_msg = "Permission denied - check if Imagen is enabled"

            return {
                "success": False,
                "error": error_msg,
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
        """
        Save image data to file

        Args:
            image_data: Raw image bytes
            filename: Name for the file
            image_type: "header" or "profile"

        Returns:
            Success status
        """
        try:
            if image_type == "header":
                filepath = self.header_dir / filename
            else:
                filepath = self.profile_dir / filename

            # Write image data to file
            with open(filepath, 'wb') as f:
                f.write(image_data)

            logger.info(f"Saved {image_type} image: {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to save image {filename}: {e}")
            return False

    def generate_batch(self, prompts: List[str], image_type: str, start_id: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of images

        Args:
            prompts: List of prompts to generate
            image_type: "header" or "profile"
            start_id: Starting ID for naming

        Returns:
            List of generation results
        """
        results = []
        aspect_ratio = "3:1" if image_type == "header" else "1:1"

        for i, prompt in enumerate(prompts):
            image_id = start_id + i
            logger.info(f"Generating {image_type} image {image_id}...")

            # Generate the image
            result = self.generate_image_with_imagen(prompt, aspect_ratio)
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

    def generate_all_images(self, num_headers: int = 150, num_profiles: int = 150):
        """
        Generate all X images

        Args:
            num_headers: Number of header images to generate
            num_profiles: Number of profile images to generate
        """
        logger.info(f"Starting generation of {num_headers} headers and {num_profiles} profiles")

        # Update stats
        self.stats["headers_requested"] = num_headers
        self.stats["profiles_requested"] = num_profiles

        all_results = []

        # Generate header prompts
        logger.info("Generating header prompts...")
        header_prompts = self.generate_header_prompts()[:num_headers]

        # Process headers in batches
        logger.info("\n===== Generating Header Images =====")
        for batch_start in range(0, num_headers, self.batch_size):
            batch_end = min(batch_start + self.batch_size, num_headers)
            batch_prompts = header_prompts[batch_start:batch_end]

            logger.info(f"Processing header batch {batch_start//self.batch_size + 1}")
            batch_results = self.generate_batch(batch_prompts, "header", batch_start + 1)
            all_results.extend(batch_results)

            # Save intermediate progress
            self.save_progress_report(all_results, f"headers_batch_{batch_start//self.batch_size + 1}")

            if batch_end < num_headers:
                logger.info(f"Pausing {self.delay_between_batches} seconds before next batch...")
                time.sleep(self.delay_between_batches)

        # Generate profile prompts
        logger.info("\nGenerating profile prompts...")
        profile_prompts = self.generate_profile_prompts()[:num_profiles]

        # Process profiles in batches
        logger.info("\n===== Generating Profile Images =====")
        for batch_start in range(0, num_profiles, self.batch_size):
            batch_end = min(batch_start + self.batch_size, num_profiles)
            batch_prompts = profile_prompts[batch_start:batch_end]

            logger.info(f"Processing profile batch {batch_start//self.batch_size + 1}")
            batch_results = self.generate_batch(batch_prompts, "profile", num_headers + batch_start + 1)
            all_results.extend(batch_results)

            # Save intermediate progress
            self.save_progress_report(all_results, f"profiles_batch_{batch_start//self.batch_size + 1}")

            if batch_end < num_profiles:
                logger.info(f"Pausing {self.delay_between_batches} seconds before next batch...")
                time.sleep(self.delay_between_batches)

        # Generate final report
        self.generate_final_report(all_results)

        return all_results

    def save_progress_report(self, results: List[Dict], batch_name: str):
        """Save intermediate progress report"""
        report = {
            "batch": batch_name,
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats.copy(),
            "results": [
                {
                    "image_id": r.get("image_id"),
                    "type": r.get("image_type"),
                    "success": r.get("success"),
                    "filename": r.get("filename"),
                    "error": r.get("error")
                }
                for r in results
            ]
        }

        report_path = self.output_dir / f"progress_{batch_name}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

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

    # Generate 150 headers and 150 profiles (total 300 images)
    results = generator.generate_all_images(num_headers=150, num_profiles=150)

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_generation()
    else:
        main()
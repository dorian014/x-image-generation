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
        """Generate diverse prompts for X header backgrounds - FUN AND VIRAL"""

        # Main subjects/scenes for variety
        scenes = [
            "interconnected floating neon islands with rainbow bridges",
            "abstract vaporwave city skyline melting into geometric shapes",
            "surreal landscape of giant floating crystals and holographic clouds",
            "cyberpunk circuit board landscape transforming into organic patterns",
            "retro arcade game world with pixelated mountains and glitch effects",
            "dreamlike space station interior with impossible M.C. Escher geometry",
            "underwater digital realm with neon coral and data streams",
            "abstract memphis-style playground with impossible physics",
            "futuristic Tokyo street scene abstracted into geometric patterns",
            "surreal desert with chrome cacti and liquid metal dunes",
            "floating digital gardens with pixelated flowers and holographic trees",
            "abstract social media universe with floating interface elements",
            "neon jungle with geometric animals and data vines",
            "retro-futuristic mall aesthetic with vaporwave elements",
            "digital storm of emoji particles and meme symbols"
        ]

        # Color palettes
        palettes = [
            "electric pink, cyan, deep purple neons",
            "pastel vaporwave pink, blue, and mint",
            "acid green, hot magenta, electric yellow",
            "deep space purple, galaxy blue, nebula pink",
            "miami vice teal and hot pink",
            "cyberpunk red, blue, and chrome",
            "rainbow holographic with iridescent effects",
            "sunset orange, purple, and gold gradients",
            "matrix green and black with glitch effects",
            "cotton candy pastels with neon accents"
        ]

        # Meme-related objects (generic, no specific brands)
        objects = [
            "floating diamond hands, rocket ships, and moon symbols",
            "abstract emoji explosions, heart reactions, fire symbols",
            "glitching pixel art creatures and retro game power-ups",
            "holographic butterflies, stars, and sparkle effects",
            "floating crystals, gems, and energy orbs",
            "abstract wifi signals, cloud symbols, and data streams",
            "geometric pizza slices, tacos, and food icons",
            "retro computer windows, cursors, and loading bars",
            "abstract money symbols, coins, and treasure chests",
            "floating planets, UFOs, and space objects",
            "rainbow prisms, laser beams, and light trails",
            "abstract cat shapes, dog patterns, and animal spirits",
            "digital flowers, mushrooms, and nature fractals",
            "geometric skulls, flames, and lightning bolts",
            "abstract crown symbols, stars, and celebration confetti"
        ]

        # Moods
        moods = [
            "chaotic but harmonious",
            "explosively vibrant",
            "dreamily surreal",
            "aggressively playful",
            "mysteriously energetic",
            "wildly optimistic",
            "beautifully chaotic",
            "hypnotically dynamic"
        ]

        enhanced_prompts = []
        for i in range(150):
            scene = random.choice(scenes)
            palette = random.choice(palettes)
            object_set = random.choice(objects)
            mood = random.choice(moods)

            prompt = f"A wide, 1500x500 pixel cartoonish background image. {scene}. Focus on {palette} color palette. Include {object_set} scattered throughout the composition. No people, no text, no brands. The overall mood should be {mood}. Allow for black padding above and below if necessary to fit the aspect ratio. Digital art style, trending design, high energy, maximum visual impact"

            enhanced_prompts.append(prompt)

        return enhanced_prompts[:150]  # Return 150 header prompts

    def generate_profile_prompts(self) -> List[str]:
        """Generate diverse prompts for X profile images - CYBERPUNK VIRAL STYLE"""

        # Main subjects/characters
        subjects = [
            "geometric wolf head",
            "abstract dragon face",
            "cybernetic cat avatar",
            "digital phoenix",
            "holographic bear spirit",
            "neon tiger mask",
            "crystalline eagle head",
            "robot samurai helmet",
            "alien consciousness orb",
            "digital demon skull",
            "cyber owl entity",
            "abstract lion mane",
            "pixelated shark jaw",
            "geometric butterfly being",
            "plasma energy creature",
            "digital octopus brain",
            "chrome skull avatar",
            "neon serpent head",
            "abstract fox spirit",
            "cyber monkey face",
            "holographic raven",
            "digital wolf pack leader",
            "geometric unicorn",
            "abstract bull head",
            "neon mantis warrior",
            "crystalline spider queen",
            "digital kraken eye",
            "cyber panda warrior",
            "abstract jellyfish mind",
            "holographic bat creature"
        ]

        # Internet/meme symbols
        meme_symbols = [
            "diamond hands, rocket emojis, and moon crescents",
            "fire emojis, 100 symbols, and explosion effects",
            "heart reactions, thumbs up, and star ratings",
            "lightning bolts, energy waves, and power symbols",
            "crown symbols, trophy icons, and winner badges",
            "pizza slices, taco patterns, and food particles",
            "WiFi signals, cloud icons, and data streams",
            "pixel hearts, game lives, and power-up symbols",
            "money bags, coin stacks, and treasure effects",
            "rainbow prisms, sparkles, and magic dust",
            "skull emojis, flame effects, and danger signs",
            "eye symbols, third eyes, and vision beams",
            "mushroom clouds, atomic symbols, and radiation",
            "infinity loops, sacred geometry, and fractals",
            "glitch artifacts, error messages, and corrupted data"
        ]

        # Color palettes
        color_combos = [
            "fuchsia, electric blue, violet",
            "hot pink, cyan, deep purple",
            "acid green, magenta, gold",
            "crimson red, neon blue, silver",
            "toxic green, hot orange, black",
            "miami pink, teal, white",
            "royal purple, emerald, gold",
            "electric yellow, hot pink, turquoise",
            "blood red, ice blue, chrome",
            "neon orange, purple, lime",
            "galaxy blue, nebula pink, star white",
            "matrix green, black, silver",
            "sunset orange, violet, indigo",
            "cotton candy pink, baby blue, lavender",
            "radioactive green, warning orange, hazard yellow"
        ]

        enhanced_prompts = []
        for i in range(150):
            subject = random.choice(subjects)
            symbols = random.choice(meme_symbols)
            colors = random.choice(color_combos)

            prompt = f"Abstract, neon-drenched digital art profile picture, centered {subject} with glowing eyes, surrounded by a chaotic yet cohesive swirling vortex of {symbols}. Vibrant cyberpunk color palette of {colors}. High detail, intricate lines, dynamic lighting, trending on ArtStation. No text, no watermarks, square format, maximum visual impact, viral aesthetic"

            enhanced_prompts.append(prompt)

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
            try:
                result = subprocess.run(['gcloud', 'auth', 'print-access-token'],
                                      capture_output=True, text=True, check=True)
                access_token = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                # Fallback: try using environment variable if set
                access_token = os.environ.get('GOOGLE_ACCESS_TOKEN')
                if not access_token:
                    logger.error(f"Failed to get access token: {e}")
                    logger.error("Try running: gcloud auth application-default login")
                    raise

            # Set image size based on aspect ratio
            if aspect_ratio == "3:1":
                # For headers - closest to 1500x500
                image_size = "1536x512"  # Actual 3:1 aspect ratio
            else:
                # For profiles - square
                image_size = "1024x1024"

            # Prepare the request payload for Imagen
            # Note: Cannot use seed with default watermark settings
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "negativePrompt": "text, watermark, logo, brand, signature, low quality, blurry, realistic photo, human, person, face, letters, words, writing",
                    "sampleImageSize": int(image_size.split('x')[0])  # Convert to integer
                    # Removed seed parameter - not compatible with watermark
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

            # Handle errors with detailed logging
            error_msg = f"API returned {response.status_code}"
            if response.status_code == 429:
                error_msg = "Rate limit exceeded"
            elif response.status_code == 403:
                error_msg = "Permission denied - check if Imagen is enabled"
            elif response.status_code == 400:
                # Log the full error for 400 responses
                try:
                    error_detail = response.json()
                    logger.error(f"400 Error Details: {error_detail}")
                    error_msg = f"Bad request: {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    error_msg = f"Bad request: {response.text[:200]}"

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
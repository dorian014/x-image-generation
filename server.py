#!/usr/bin/env python3
"""
Simple HTTP server for X Image Generator
Run this to use the web interface
"""

import http.server
import socketserver
import json
import threading
import time
import os
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Import our image generator
from x_image_generator import XImageGenerator

PORT = 8888

class ImageGeneratorHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for image generation"""

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # Serve the index.html file
            self.serve_html()
        elif parsed_path.path == '/favicon.ico':
            # Handle favicon request (return empty for now)
            self.send_response(204)  # No Content
            self.end_headers()
        elif parsed_path.path == '/status':
            # Check server status
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'running'}).encode())
        elif parsed_path.path == '/generate':
            # Handle image generation with SSE
            self.handle_generation(parsed_path)
        else:
            # Serve static files
            try:
                super().do_GET()
            except:
                self.send_error(404, "File not found")

    def serve_html(self):
        """Serve the index.html file"""
        try:
            with open('index.html', 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "index.html not found")

    def handle_generation(self, parsed_path):
        """Handle image generation request with Server-Sent Events"""
        # Parse query parameters
        params = parse_qs(parsed_path.query)
        num_headers = int(params.get('headers', [150])[0])
        num_profiles = int(params.get('profiles', [150])[0])
        header_folder = params.get('headerFolder', ['generated_images/headers'])[0]
        profile_folder = params.get('profileFolder', ['generated_images/profiles'])[0]

        # Set up SSE headers
        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        # Start generation in a thread
        generator_thread = threading.Thread(
            target=self.run_generation,
            args=(num_headers, num_profiles, header_folder, profile_folder)
        )
        generator_thread.daemon = True
        generator_thread.start()

    def run_generation(self, num_headers, num_profiles, header_folder, profile_folder):
        """Run the image generation and send progress updates"""
        try:
            # Send initial status
            self.send_sse_message({
                'type': 'status',
                'message': 'Initializing Vertex AI...'
            })

            # Create generator instance with custom folders
            generator = XImageGeneratorWithProgress(self, header_folder, profile_folder)

            # Generate images
            self.send_sse_message({
                'type': 'status',
                'message': f'Starting generation of {num_headers} headers and {num_profiles} profiles...'
            })

            results = generator.generate_all_images(num_headers, num_profiles)

            # Send completion message
            summary = {
                'headers_requested': num_headers,
                'headers_successful': generator.stats['headers_successful'],
                'profiles_requested': num_profiles,
                'profiles_successful': generator.stats['profiles_successful'],
                'success_rate': f"{((generator.stats['headers_successful'] + generator.stats['profiles_successful']) / (num_headers + num_profiles) * 100):.1f}%",
                'output_directory': f"Headers: {generator.header_dir.absolute()}, Profiles: {generator.profile_dir.absolute()}"
            }

            self.send_sse_message({
                'type': 'complete',
                'summary': summary
            })

        except Exception as e:
            self.send_sse_message({
                'type': 'error',
                'message': str(e)
            })

    def send_sse_message(self, data):
        """Send a Server-Sent Event message"""
        try:
            message = f"data: {json.dumps(data)}\n\n"
            self.wfile.write(message.encode())
            self.wfile.flush()
        except Exception as e:
            print(f"Error sending SSE message: {e}")

    def log_message(self, format, *args):
        """Override to reduce console spam"""
        if args and isinstance(args[0], str):
            if '/generate' in args[0] or '/status' in args[0] or 'favicon' in args[0]:
                pass  # Don't log these requests
        else:
            super().log_message(format, *args)


class XImageGeneratorWithProgress(XImageGenerator):
    """Extended generator that sends progress updates"""

    def __init__(self, handler, header_folder=None, profile_folder=None):
        super().__init__()
        self.handler = handler

        # Override default folders if custom ones provided
        if header_folder:
            self.header_dir = Path(header_folder)
            self.header_dir.mkdir(parents=True, exist_ok=True)
        if profile_folder:
            self.profile_dir = Path(profile_folder)
            self.profile_dir.mkdir(parents=True, exist_ok=True)

    def generate_batch(self, prompts, image_type, start_id):
        """Override to send progress updates"""
        results = []
        aspect_ratio = "3:1" if image_type == "header" else "1:1"

        for i, prompt in enumerate(prompts):
            image_id = start_id + i

            # Send status update
            self.handler.send_sse_message({
                'type': 'status',
                'message': f'Generating {image_type} image {image_id}...'
            })

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

            # Send progress update
            self.handler.send_sse_message({
                'type': 'progress',
                'imageId': image_id,
                'imageType': image_type,
                'success': result["success"],
                'error': result.get("error", None)
            })

            results.append(result)

            # Rate limiting
            if i < len(prompts) - 1:
                time.sleep(self.delay_between_images)

        return results


def main():
    """Start the server"""
    print("\n" + "="*60)
    print("🎨 X Image Generator - Web Interface")
    print("="*60)

    # Check if gcloud is authenticated
    import subprocess
    try:
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'],
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("✅ Google Cloud authentication detected")
        else:
            print("⚠️  Warning: Google Cloud authentication may not be configured")
            print("   Run: gcloud auth application-default login")
    except:
        print("⚠️  Warning: gcloud CLI not found or not authenticated")
        print("   Install gcloud and run: gcloud auth application-default login")

    print(f"\n🚀 Starting server on http://localhost:{PORT}")
    print("📝 Open your browser to http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server\n")
    print("-"*60)

    # Change to the script directory
    os.chdir(Path(__file__).parent)

    # Start the server
    with socketserver.TCPServer(("", PORT), ImageGeneratorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✋ Server stopped")
            return


if __name__ == "__main__":
    main()
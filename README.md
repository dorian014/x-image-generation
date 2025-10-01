# X (Twitter) Image Generator

Generate cartoon-style images for X (Twitter) using Google Vertex AI's Imagen model.

## Features

- Generate 1500x500 header backgrounds (with letterboxing if needed)
- Generate square profile images
- Cartoon/vector art style
- No people, text, or brands
- Batch processing with rate limiting
- Automatic retry logic
- Progress tracking and reporting

## Prerequisites

1. Google Cloud Project with Vertex AI enabled
2. Authentication set up for Google Cloud

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google Cloud Authentication

You need to authenticate with Google Cloud. Choose one of these methods:

#### Option A: Use gcloud CLI (Recommended)

```bash
# Install gcloud CLI if you haven't already
# https://cloud.google.com/sdk/docs/install

# Login to your Google Cloud account
gcloud auth login

# Set your project
gcloud config set project qstarlabs-dev

# Get application default credentials
gcloud auth application-default login
```

#### Option B: Use Service Account

```bash
# Create and download a service account key from Google Cloud Console
# Save it as credentials.json in this directory

export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
```

### 3. Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Storage API (if using)
gcloud services enable storage.googleapis.com
```

## Usage

### Test Generation (2 headers + 2 profiles)

```bash
python x_image_generator.py test
```

### Full Generation (150 headers + 150 profiles = 300 total)

```bash
python x_image_generator.py
```

## Output

Images will be saved in the `generated_images/` directory:

```
generated_images/
├── headers/          # 1500x500 header images
│   ├── header_001.png
│   ├── header_002.png
│   └── ...
├── profiles/         # Square profile images
│   ├── profile_001.png
│   ├── profile_002.png
│   └── ...
└── final_report_*.json  # Generation report
```

## Configuration

Edit the `XImageGenerator` class in `x_image_generator.py` to adjust:

- `project_id`: Your Google Cloud project ID (default: "qstarlabs-dev")
- `batch_size`: Number of images per batch (default: 5)
- `delay_between_images`: Seconds between each image (default: 3)
- `delay_between_batches`: Seconds between batches (default: 15)

## Rate Limits

The script implements automatic rate limiting to avoid hitting Vertex AI quotas:
- 3 seconds between individual image generations
- 15 seconds pause between batches
- Automatic retry with exponential backoff on rate limit errors

## Troubleshooting

### Authentication Issues

If you get authentication errors, ensure:
1. You're logged in with `gcloud auth login`
2. Application default credentials are set: `gcloud auth application-default login`
3. Your project has billing enabled

### Quota Errors

If you hit quota limits:
1. Reduce `batch_size` in the script
2. Increase delays between images
3. Check your Vertex AI quotas in Google Cloud Console

### Model Access

If you can't access the Imagen model:
1. Ensure Vertex AI API is enabled
2. Check if Imagen is available in your region (us-central1 recommended)
3. Verify your project has access to Imagen 3

## Cost Estimation

Imagen 3 pricing (as of 2024):
- ~$0.040 per image for standard quality
- 300 images ≈ $12.00

Check current pricing at: https://cloud.google.com/vertex-ai/pricing

## License

MIT
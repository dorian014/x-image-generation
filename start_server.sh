#!/bin/bash

echo "🔐 Setting up authentication for X Image Generator..."

# Get the current access token and refresh it periodically
export GOOGLE_ACCESS_TOKEN=$(gcloud auth print-access-token 2>/dev/null)

if [ -z "$GOOGLE_ACCESS_TOKEN" ]; then
    echo "❌ Failed to get Google Cloud access token"
    echo "Please run: gcloud auth login"
    exit 1
fi

echo "✅ Authentication successful"
echo "📂 Current account: $(gcloud config get-value account)"
echo "📂 Current project: $(gcloud config get-value project)"
echo "🚀 Starting server on http://localhost:8888"
echo ""

# Refresh token every 30 minutes in background
(
    while true; do
        sleep 1800  # 30 minutes
        export GOOGLE_ACCESS_TOKEN=$(gcloud auth print-access-token 2>/dev/null)
        echo "🔄 Refreshed authentication token"
    done
) &

# Start the Python server with the token in environment
python server.py
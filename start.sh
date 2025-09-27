#!/bin/bash

# EdTrack Startup Script for Railway
echo "🚀 Starting EdTrack on Railway..."

# Set environment variables for Streamlit
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Start Streamlit
echo "📱 Starting Streamlit server on port $PORT..."
streamlit run streamlit_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.runOnSave=false \
  --browser.gatherUsageStats=false

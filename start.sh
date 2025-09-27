#!/bin/bash

# EdTrack Startup Script for Railway
echo "🚀 Starting EdTrack on Railway..."

# Start Streamlit
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true

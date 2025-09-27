#!/bin/bash

# EdTrack Startup Script for Railway
echo "🚀 Starting EdTrack on Railway..."

# Initialize database if tables don't exist
echo "🗄️ Initializing database..."
python init_db.py

# Start Streamlit
echo "📱 Starting Streamlit server..."
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true

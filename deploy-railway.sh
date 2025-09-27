#!/bin/bash

# EdTrack Railway Deployment Script
set -e

echo "🚂 EdTrack Railway Deployment Setup"
echo "=================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    
    # Detect OS and install Railway CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install railway
        else
            echo "❌ Please install Homebrew first: https://brew.sh"
            echo "   Then run: brew install railway"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://railway.app/install.sh | sh
    else
        echo "❌ Unsupported OS. Please install Railway CLI manually:"
        echo "   https://docs.railway.app/develop/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI is installed"

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project or link to existing
echo "🚂 Setting up Railway project..."
echo "Choose an option:"
echo "1) Create new project"
echo "2) Link to existing project"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "📝 Creating new Railway project..."
    railway project create
else
    echo "🔗 Linking to existing project..."
    railway link
fi

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set PYTHON_VERSION=3.10
railway variables set PORT=8501

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo "🌐 Your app will be available at: https://your-app.railway.app"
echo ""
echo "📋 Next steps:"
echo "1. Wait for deployment to complete (2-3 minutes)"
echo "2. Initialize your database by running:"
echo "   railway run python init_db.py"
echo "3. Check logs with: railway logs"
echo ""
echo "🔧 Useful Railway commands:"
echo "  railway status          - Check deployment status"
echo "  railway logs            - View application logs"
echo "  railway variables       - Manage environment variables"
echo "  railway run python init_db.py - Initialize database"
echo "  railway open            - Open your app in browser"

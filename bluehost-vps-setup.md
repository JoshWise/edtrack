# Bluehost VPS Deployment Guide

If you want to deploy EdTrack on Bluehost VPS (not shared hosting), here's how:

## Prerequisites
- Bluehost VPS plan ($20+/month)
- Root access to your VPS
- Domain name pointing to your VPS IP

## Setup Steps

### 1. Connect to Your VPS
```bash
ssh root@your-vps-ip
```

### 2. Install Docker
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker $USER
```

### 3. Deploy EdTrack
```bash
# Clone your repository
git clone https://github.com/yourusername/edtrack.git
cd edtrack

# Deploy with Docker
./deploy.sh
```

### 4. Configure Domain
```bash
# Install nginx for reverse proxy
apt install nginx -y

# Create nginx config
cat > /etc/nginx/sites-available/edtrack << EOF
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/edtrack /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 5. SSL Certificate (Optional)
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d yourdomain.com
```

## Cost Comparison
- Bluehost Shared: $3-10/month (❌ Won't work)
- Bluehost VPS: $20+/month (✅ Will work but expensive)
- Streamlit Cloud: $0/month (✅ Perfect and free)
- Railway: $5/month (✅ Better value)
- Render: $7/month (✅ Better value)

# 🚀 EdTrack Deployment Guide

This guide covers multiple deployment options for your EdTrack application.

## 📋 Prerequisites

- Python 3.10+ (already configured)
- Docker & Docker Compose (for containerized deployment)
- Git (for version control)

## 🎯 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Easiest)

**Perfect for:**
- Quick deployment
- Free hosting
- Automatic GitHub integration

**Steps:**
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set your database URL in secrets:
     ```
     DATABASE_URL = "postgresql+psycopg2://user:pass@host:5432/edtrack"
     ```

3. **Your app will be live!** 🎉

### Option 2: Docker Deployment (Full Control)

**Perfect for:**
- Custom hosting
- Linode/VPS deployment
- Production environments

**Quick Deploy:**
```bash
./deploy.sh
```

**Manual Deploy:**
```bash
# 1. Create environment file
echo "POSTGRES_PASSWORD=your-secure-password" > .env

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Initialize database
docker-compose -f docker-compose.prod.yml exec app python init_db.py
```

**Access your app:** http://localhost:8501

### Option 3: Linode/VPS Deployment

**Perfect for:**
- Your own server
- Custom domain
- Full control

**Steps:**
1. **Create Linode instance** (Ubuntu 22.04 LTS)
2. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Clone and deploy:**
   ```bash
   git clone https://github.com/yourusername/edtrack.git
   cd edtrack
   ./deploy.sh
   ```

4. **Configure domain** (optional):
   - Point your domain to Linode IP
   - Add reverse proxy (nginx) for HTTPS

### Option 4: Railway/Render (Managed Cloud)

**Perfect for:**
- Managed PostgreSQL
- Automatic deployments
- Built-in monitoring

**Railway:**
1. Connect GitHub repository
2. Add PostgreSQL service
3. Set environment variables
4. Deploy automatically

**Render:**
1. Create new Web Service
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `streamlit run streamlit_app.py`

## 🔧 Configuration

### Environment Variables

Your app supports these environment variables:

```bash
# Database (required for production)
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname

# Optional: Custom settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=edtrack
```

### Streamlit Configuration

For custom Streamlit settings, create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 🗄️ Database Setup

### Production Database Options:

1. **Managed PostgreSQL:**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database
   - Supabase
   - Railway PostgreSQL

2. **Self-hosted PostgreSQL:**
   - Docker container (included in docker-compose)
   - Linode VPS
   - DigitalOcean Droplet

### Database Migration:

Your app automatically creates tables on first run with `init_db.py`. For production:

```bash
# Initialize with sample data
python init_db.py

# Or initialize empty database
python -c "
from db import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database schema created')
"
```

## 🔒 Security Considerations

### Production Checklist:

- [ ] Use strong database passwords
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Set up proper firewall rules
- [ ] Regular database backups
- [ ] Monitor application logs
- [ ] Use environment variables for secrets

### Security Commands:

```bash
# Generate secure password
openssl rand -base64 32

# Create secure .env file
cat > .env << EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
EOF
```

## 📊 Monitoring & Maintenance

### Health Checks:

Your Docker setup includes health checks:
```bash
# Check app health
curl http://localhost:8501/_stcore/health

# Check container status
docker-compose -f docker-compose.prod.yml ps
```

### Logs:

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f app

# View database logs
docker-compose -f docker-compose.prod.yml logs -f db
```

### Backup:

```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres edtrack > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres edtrack < backup.sql
```

## 🚨 Troubleshooting

### Common Issues:

1. **Database Connection Error:**
   - Check DATABASE_URL format
   - Verify database is running
   - Check firewall/network access

2. **Port Already in Use:**
   - Change port in docker-compose.yml
   - Kill existing processes: `sudo lsof -ti:8501 | xargs kill -9`

3. **Permission Errors:**
   - Check file permissions
   - Ensure Docker user has access

### Debug Commands:

```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs app

# Access container shell
docker-compose -f docker-compose.prod.yml exec app bash

# Check database connection
docker-compose -f docker-compose.prod.yml exec app python -c "from db import engine; print(engine.url)"
```

## 🎉 Success!

Your EdTrack application is now deployment-ready! Choose the option that best fits your needs:

- **Quick start:** Streamlit Cloud
- **Full control:** Docker deployment
- **Production:** Linode/VPS with Docker
- **Managed:** Railway/Render

Remember to update your Linode domain version as well! [[memory:8793481]]

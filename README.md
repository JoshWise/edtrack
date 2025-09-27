# EdTrack — Educational Tracking System

A modern Streamlit application for tracking classes, lessons, learning targets, and student progress.

## 🚀 Quick Start (Development)

### 1) Start Postgres (Docker)
```bash
docker compose up -d
```

### 2) Python env (Python 3.10+)
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Init DB
```bash
python init_db.py   # creates tables + seeds sample data
```

### 4) Run UI
```bash
streamlit run streamlit_app.py
```

### 5) Stop Postgres
```bash
docker compose down
```

## 🌐 Deployment Options

### Streamlit Cloud (Easiest)
- Push to GitHub
- Deploy at [share.streamlit.io](https://share.streamlit.io)
- Set `DATABASE_URL` in secrets

### Docker (Full Control)
```bash
./deploy.sh
```

### Production Server
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide including Linode setup.

## 📋 Features

- **Dashboard**: Overview of schools, teachers, students, classes, lessons, and targets
- **Data Management**: Add schools, teachers, students, and classes
- **Lesson Planning**: Create lessons and map learning targets
- **Progress Tracking**: Record student progress on learning targets
- **Reports**: Mastery tracking and student progress timelines

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy 2.0+
- **Deployment**: Docker, Streamlit Cloud, or custom hosting

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Database Schema](models.py) - Data model definitions
- [API Documentation](db.py) - Database configuration

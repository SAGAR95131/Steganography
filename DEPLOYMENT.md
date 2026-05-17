# CyberCloak Deployment Guide

## Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///instance/cybercloak.db

# Security
SESSION_SECRET=your-super-secret-key-change-this-in-production

# OAuth Configuration (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email Configuration (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key
ADMIN_EMAIL=admin@example.com

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Application**
   Open http://localhost:5000 in your browser

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-production-secret-key
```

## Features Overview

✅ **Completed Features:**
- Modern responsive UI with multiple themes
- User authentication (OAuth + Demo access)
- Complete navigation system
- User profile management
- Activity tracking
- Help center with FAQ
- About page with team info
- Legal pages (Privacy Policy, Terms of Service)
- Enhanced dashboard with statistics
- Mobile-friendly design
- Security features and validation

🚀 **Ready to Use:**
- All pages are linked and functional
- Professional header and footer
- Working authentication system
- Complete user experience flow
- Responsive design for all devices

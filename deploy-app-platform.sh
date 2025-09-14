#!/bin/bash

# Digital Ocean App Platform Deployment Script
# This creates a simple deployment using Digital Ocean's App Platform

echo "🌊 Digital Ocean App Platform Deployment"
echo "========================================"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl (Digital Ocean CLI) is not installed"
    echo ""
    echo "To install doctl:"
    echo "1. Download from: https://github.com/digitalocean/doctl/releases"
    echo "2. Or install via package manager:"
    echo "   - macOS: brew install doctl"
    echo "   - Ubuntu: snap install doctl"
    echo "   - Windows: choco install doctl"
    echo ""
    echo "After installing, authenticate with: doctl auth init"
    exit 1
fi

# Check if user is authenticated
if ! doctl account get &> /dev/null; then
    echo "❌ Not authenticated with Digital Ocean"
    echo "Please run: doctl auth init"
    exit 1
fi

echo "✅ Authenticated with Digital Ocean"

# Create app spec
echo "📝 Creating app specification..."
cat > app.yaml << 'EOF'
name: hospital-system
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo-name
    branch: main
  run_command: gunicorn hospital_system.wsgi:application --bind 0.0.0.0:8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  routes:
  - path: /
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key-here"
  - key: ALLOWED_HOSTS
    value: "your-app-name.ondigitalocean.app"
  - key: USE_POSTGRESQL
    value: "True"
  - key: DB_NAME
    value: "hospital_db"
  - key: DB_USER
    value: "hospital_user"
  - key: DB_PASSWORD
    value: "your-db-password"
  - key: DB_HOST
    value: "your-db-host"
  - key: DB_PORT
    value: "5432"
  - key: REDIS_URL
    value: "your-redis-url"

databases:
- name: hospital-db
  engine: PG
  version: "15"
  size: db-s-1vcpu-1gb
  num_nodes: 1
EOF

echo "📋 App specification created in app.yaml"
echo ""
echo "Next steps:"
echo "1. Update app.yaml with your GitHub repository details"
echo "2. Update environment variables with your actual values"
echo "3. Run: doctl apps create --spec app.yaml"
echo ""
echo "Or use the Digital Ocean web interface:"
echo "1. Go to Apps in your Digital Ocean dashboard"
echo "2. Click 'Create App'"
echo "3. Connect your GitHub repository"
echo "4. Configure the settings as shown in app.yaml"

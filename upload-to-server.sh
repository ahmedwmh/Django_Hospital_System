#!/bin/bash

# Script to upload project files to Digital Ocean droplet
# Usage: ./upload-to-server.sh your-droplet-ip

if [ -z "$1" ]; then
    echo "❌ Please provide your Digital Ocean droplet IP address"
    echo "Usage: ./upload-to-server.sh YOUR_DROPLET_IP"
    exit 1
fi

DROPLET_IP=$1
USER="hospital"

echo "🚀 Uploading Hospital System to Digital Ocean droplet at $DROPLET_IP"

# Create the directory on the server
echo "📁 Creating directory on server..."
ssh $USER@$DROPLET_IP "sudo mkdir -p /var/www/hospital_system && sudo chown $USER:$USER /var/www/hospital_system"

# Upload all project files
echo "📤 Uploading project files..."
rsync -avz --exclude='venv/' --exclude='__pycache__/' --exclude='.git/' --exclude='db.sqlite3' --exclude='*.pyc' ./ $USER@$DROPLET_IP:/var/www/hospital_system/

echo "✅ Upload completed!"
echo ""
echo "Next steps:"
echo "1. SSH into your droplet: ssh $USER@$DROPLET_IP"
echo "2. Navigate to project: cd /var/www/hospital_system"
echo "3. Run deployment: ./deploy.sh"

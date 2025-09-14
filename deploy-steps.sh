#!/bin/bash

# Complete deployment script for Digital Ocean
# This script will guide you through the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if droplet IP is provided
if [ -z "$1" ]; then
    print_error "Please provide your Digital Ocean droplet IP address"
    echo "Usage: ./deploy-steps.sh YOUR_DROPLET_IP [DOMAIN_NAME]"
    echo "Example: ./deploy-steps.sh 123.456.789.012 yourdomain.com"
    exit 1
fi

DROPLET_IP=$1
DOMAIN=${2:-""}
USER="hospital"

echo "🏥 Hospital System Deployment to Digital Ocean"
echo "=============================================="
echo "Droplet IP: $DROPLET_IP"
if [ ! -z "$DOMAIN" ]; then
    echo "Domain: $DOMAIN"
fi
echo ""

# Step 1: Check if we can connect to the droplet
print_step "1. Testing connection to droplet..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $USER@$DROPLET_IP exit 2>/dev/null; then
    print_error "Cannot connect to $USER@$DROPLET_IP"
    print_warning "Please make sure:"
    print_warning "1. Your droplet is running"
    print_warning "2. You have SSH access set up"
    print_warning "3. The user 'hospital' exists on the droplet"
    print_warning ""
    print_warning "To set up the user, run on your droplet:"
    print_warning "sudo adduser hospital"
    print_warning "sudo usermod -aG sudo hospital"
    exit 1
fi
print_success "Connection successful!"

# Step 2: Upload project files
print_step "2. Uploading project files..."
if command -v rsync &> /dev/null; then
    rsync -avz --exclude='venv/' --exclude='__pycache__/' --exclude='.git/' --exclude='db.sqlite3' --exclude='*.pyc' ./ $USER@$DROPLET_IP:/var/www/hospital_system/
else
    print_warning "rsync not found, using scp instead..."
    scp -r ./* $USER@$DROPLET_IP:/var/www/hospital_system/
fi
print_success "Files uploaded!"

# Step 3: Run deployment on server
print_step "3. Running deployment on server..."
ssh $USER@$DROPLET_IP << 'EOF'
cd /var/www/hospital_system
chmod +x deploy.sh setup-ssl.sh docker-entrypoint.sh
./deploy.sh
EOF
print_success "Server setup completed!"

# Step 4: Configure environment
print_step "4. Configuring environment..."
ssh $USER@$DROPLET_IP << 'EOF'
cd /var/www/hospital_system
cp env.production .env

# Generate a secure secret key
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Update .env file with generated secret key
sed -i "s/your-very-secure-secret-key-here-change-this/$SECRET_KEY/" .env

# Update allowed hosts
sed -i "s/your-droplet-ip/$(curl -s ifconfig.me)/" .env

echo "Environment configured with secure secret key"
EOF
print_success "Environment configured!"

# Step 5: Set up SSL if domain provided
if [ ! -z "$DOMAIN" ]; then
    print_step "5. Setting up SSL certificate for $DOMAIN..."
    ssh $USER@$DROPLET_IP << EOF
cd /var/www/hospital_system
./setup-ssl.sh $DOMAIN
EOF
    print_success "SSL certificate set up!"
else
    print_warning "No domain provided, skipping SSL setup"
    print_warning "You can set up SSL later by running: ./setup-ssl.sh your-domain.com"
fi

# Step 6: Start the application
print_step "6. Starting the application..."
ssh $USER@$DROPLET_IP << 'EOF'
cd /var/www/hospital_system
docker-compose -f docker-compose.prod.yml up -d
EOF
print_success "Application started!"

# Step 7: Wait for services to be ready
print_step "7. Waiting for services to be ready..."
sleep 30

# Step 8: Check application status
print_step "8. Checking application status..."
ssh $USER@$DROPLET_IP << 'EOF'
cd /var/www/hospital_system
echo "=== Docker Services Status ==="
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=== Application Health Check ==="
curl -f http://localhost/health/ && echo "✅ Application is healthy!" || echo "❌ Application health check failed"
EOF

# Step 9: Display access information
print_step "9. Deployment Summary"
echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "====================="
echo "🌐 Application URL: http://$DROPLET_IP"
if [ ! -z "$DOMAIN" ]; then
    echo "🌐 Domain URL: https://$DOMAIN"
fi
echo "🔐 Admin Panel: http://$DROPLET_IP/admin/"
echo "👤 Admin Username: admin"
echo "🔑 Admin Password: admin123"
echo ""
echo "📊 Useful Commands:"
echo "=================="
echo "View logs: ssh $USER@$DROPLET_IP 'cd /var/www/hospital_system && docker-compose -f docker-compose.prod.yml logs -f'"
echo "Restart app: ssh $USER@$DROPLET_IP 'cd /var/www/hospital_system && docker-compose -f docker-compose.prod.yml restart'"
echo "Update app: ssh $USER@$DROPLET_IP 'cd /var/www/hospital_system && git pull && docker-compose -f docker-compose.prod.yml up -d --build'"
echo ""
print_warning "⚠️  Important Security Notes:"
print_warning "1. Change the admin password immediately"
print_warning "2. Update database passwords in .env file"
print_warning "3. Set up regular backups"
print_warning "4. Monitor your application logs"

#!/bin/bash

# SSL Certificate Setup Script for Digital Ocean
# Run this script after your domain is pointing to your droplet

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if domain is provided
if [ -z "$1" ]; then
    print_error "Please provide your domain name as an argument"
    echo "Usage: ./setup-ssl.sh your-domain.com"
    exit 1
fi

DOMAIN=$1

print_status "Setting up SSL certificate for $DOMAIN..."

# Stop nginx if running
sudo systemctl stop nginx

# Create temporary nginx config for SSL setup
sudo tee /etc/nginx/sites-available/hospital_temp > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        return 200 'SSL setup in progress...';
        add_header Content-Type text/plain;
    }
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
}
EOF

# Enable the temporary site
sudo ln -sf /etc/nginx/sites-available/hospital_temp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start nginx
sudo systemctl start nginx

# Obtain SSL certificate
print_status "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot certonly --webroot -w /var/www/html -d $DOMAIN -d www.$DOMAIN --email admin@$DOMAIN --agree-tos --non-interactive

# Copy certificates to application directory
print_status "Copying SSL certificates..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /var/www/hospital_system/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /var/www/hospital_system/ssl/key.pem
sudo chown $USER:$USER /var/www/hospital_system/ssl/*.pem

# Update nginx configuration with domain
print_status "Updating nginx configuration..."
sed -i "s/your-domain.com/$DOMAIN/g" /var/www/hospital_system/nginx.prod.conf

# Stop temporary nginx
sudo systemctl stop nginx

# Remove temporary site
sudo rm -f /etc/nginx/sites-enabled/hospital_temp

print_status "✅ SSL certificate setup completed!"
print_warning "Don't forget to:"
print_warning "1. Update your .env file with the correct domain"
print_warning "2. Start your application with: docker-compose -f docker-compose.prod.yml up -d"
print_warning "3. Set up automatic certificate renewal with: sudo crontab -e"
print_warning "   Add this line: 0 12 * * * /usr/bin/certbot renew --quiet"

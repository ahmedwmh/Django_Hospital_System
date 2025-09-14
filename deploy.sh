#!/bin/bash

# Hospital System Deployment Script for Digital Ocean
# Run this script on your Digital Ocean droplet

set -e

echo "🏥 Starting Hospital System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /var/www/hospital_system
sudo chown $USER:$USER /var/www/hospital_system

# Configure PostgreSQL
print_status "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE USER hospital_user WITH PASSWORD 'your-secure-db-password';"
sudo -u postgres psql -c "CREATE DATABASE hospital_db OWNER hospital_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_user;"

# Configure Redis
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure UFW firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Configure fail2ban
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create SSL directory
sudo mkdir -p /var/www/hospital_system/ssl

print_status "✅ System setup completed!"
print_warning "Please remember to:"
print_warning "1. Update the .env file with your actual configuration"
print_warning "2. Set up SSL certificates"
print_warning "3. Configure your domain name"
print_warning "4. Update database passwords"
print_warning "5. Restart your session to apply Docker group changes"

echo ""
print_status "Next steps:"
echo "1. Copy your project files to /var/www/hospital_system/"
echo "2. Update the .env file with your configuration"
echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "4. Set up SSL certificates with: sudo certbot --nginx"

#!/bin/bash

# Script to update IP addresses in your project
# Usage: ./update-ips.sh PUBLIC_IP DATABASE_IP

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ Please provide both IP addresses"
    echo "Usage: ./update-ips.sh PUBLIC_IP DATABASE_IP"
    echo "Example: ./update-ips.sh 162.159.140.98 172.66.0.96"
    exit 1
fi

PUBLIC_IP=$1
DATABASE_IP=$2

echo "🔧 Updating IP addresses in your project..."
echo "Public IP: $PUBLIC_IP"
echo "Database IP: $DATABASE_IP"

# Update .env file
if [ -f ".env" ]; then
    echo "📝 Updating .env file..."
    sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1/" .env
    sed -i.bak "s/DB_HOST=.*/DB_HOST=$DATABASE_IP/" .env
    echo "✅ .env file updated"
else
    echo "⚠️  .env file not found, creating one..."
    cp env.production .env
    sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1/" .env
    sed -i.bak "s/DB_HOST=.*/DB_HOST=$DATABASE_IP/" .env
    echo "✅ .env file created and updated"
fi

# Update production environment file
echo "📝 Updating env.production file..."
sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1/" env.production
sed -i.bak "s/DB_HOST=.*/DB_HOST=$DATABASE_IP/" env.production
echo "✅ env.production file updated"

# Update nginx configuration
echo "📝 Updating nginx configuration..."
sed -i.bak "s/server_name .*/server_name $PUBLIC_IP;/" nginx.prod.conf
echo "✅ nginx configuration updated"

# Update docker-compose production
echo "📝 Updating docker-compose production..."
sed -i.bak "s/DB_HOST=.*/DB_HOST=$DATABASE_IP/" docker-compose.prod.yml
echo "✅ docker-compose production updated"

echo ""
echo "🎉 All IP addresses updated successfully!"
echo ""
echo "📋 Updated files:"
echo "- .env"
echo "- env.production"
echo "- nginx.prod.conf"
echo "- docker-compose.prod.yml"
echo ""
echo "🔄 Next steps:"
echo "1. Commit and push changes: git add . && git commit -m 'Update IP addresses' && git push"
echo "2. Redeploy your app on Digital Ocean"
echo "3. Your app will be accessible at: http://$PUBLIC_IP"

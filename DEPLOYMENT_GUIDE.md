# 🏥 Hospital System - Digital Ocean Deployment Guide

## Prerequisites
- Digital Ocean Droplet (Ubuntu 20.04 or 22.04)
- Domain name pointing to your droplet IP
- SSH access to your droplet

## Step 1: Initial Server Setup

### 1.1 Connect to your droplet
```bash
ssh root@your-droplet-ip
```

### 1.2 Create a non-root user
```bash
adduser hospital
usermod -aG sudo hospital
su - hospital
```

### 1.3 Update system packages
```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Dependencies

### 2.1 Run the deployment script
```bash
# Upload your project files to the server first
# Then run:
chmod +x deploy.sh
./deploy.sh
```

### 2.2 Logout and login again (to apply Docker group changes)
```bash
exit
ssh hospital@your-droplet-ip
```

## Step 3: Upload Your Project

### 3.1 Upload project files
You can use SCP, SFTP, or Git to upload your project:

**Option A: Using SCP (from your local machine)**
```bash
scp -r /path/to/your/project hospital@your-droplet-ip:/var/www/hospital_system/
```

**Option B: Using Git (on the server)**
```bash
cd /var/www/hospital_system
git clone https://github.com/your-username/your-repo.git .
```

## Step 4: Configure Environment

### 4.1 Copy and edit environment file
```bash
cd /var/www/hospital_system
cp env.production .env
nano .env
```

### 4.2 Update the .env file with your settings:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-droplet-ip

USE_POSTGRESQL=True
DB_NAME=hospital_db
DB_USER=hospital_user
DB_PASSWORD=your-secure-db-password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

# Update with your email settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Step 5: Set Up SSL Certificate

### 5.1 Run SSL setup script
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh your-domain.com
```

## Step 6: Deploy the Application

### 6.1 Start the application
```bash
cd /var/www/hospital_system
docker-compose -f docker-compose.prod.yml up -d
```

### 6.2 Check if everything is running
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

## Step 7: Verify Deployment

### 7.1 Check application health
```bash
curl http://localhost/health/
curl https://your-domain.com/health/
```

### 7.2 Access admin panel
Visit: `https://your-domain.com/admin/`
- Username: `admin`
- Password: `admin123`

## Step 8: Post-Deployment Tasks

### 8.1 Set up automatic certificate renewal
```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 8.2 Set up log rotation
```bash
sudo nano /etc/logrotate.d/hospital-system
```

Add:
```
/var/www/hospital_system/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 hospital hospital
}
```

### 8.3 Set up monitoring (optional)
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs
```

## Step 9: Backup Strategy

### 9.1 Create backup script
```bash
nano /var/www/hospital_system/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/hospital_system"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U hospital_user hospital_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/hospital_system/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 9.2 Make it executable and add to cron
```bash
chmod +x /var/www/hospital_system/backup.sh
crontab -e
# Add: 0 2 * * * /var/www/hospital_system/backup.sh
```

## Troubleshooting

### Common Issues:

1. **Database connection error**
   ```bash
   sudo -u postgres psql -c "SELECT 1;"
   docker-compose -f docker-compose.prod.yml logs db
   ```

2. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo nginx -t
   ```

3. **Application not starting**
   ```bash
   docker-compose -f docker-compose.prod.yml logs web
   ```

4. **Static files not loading**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```

### Useful Commands:

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Access application shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Run Django commands
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Security Checklist

- [ ] Changed default database passwords
- [ ] Set up SSL certificate
- [ ] Configured firewall (UFW)
- [ ] Set up fail2ban
- [ ] Updated secret key
- [ ] Set up regular backups
- [ ] Configured log rotation
- [ ] Set up monitoring

## Performance Optimization

1. **Enable Redis caching**
2. **Configure CDN for static files**
3. **Set up database indexing**
4. **Configure Gunicorn workers based on CPU cores**
5. **Enable Nginx gzip compression**

## Support

If you encounter any issues:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify configuration: `docker-compose -f docker-compose.prod.yml config`
3. Test database connection: `docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell`

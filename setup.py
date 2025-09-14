#!/usr/bin/env python
"""
Setup script for Hospital Management System
"""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_environment():
    """Set up the environment"""
    print("🏥 Hospital Management System Setup")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('media', exist_ok=True)
    os.makedirs('locale', exist_ok=True)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        if os.path.exists('env.example'):
            with open('env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ .env file created")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Ensure USE_POSTGRESQL=False for development
    print("🔧 Configuring database settings...")
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace USE_POSTGRESQL=True with False if it exists
        if 'USE_POSTGRESQL=True' in content:
            content = content.replace('USE_POSTGRESQL=True', 'USE_POSTGRESQL=False')
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ Database configured for SQLite (development)")
        elif 'USE_POSTGRESQL=False' in content:
            print("✅ Database already configured for SQLite")
        else:
            print("⚠️ USE_POSTGRESQL setting not found, using SQLite by default")
    except Exception as e:
        print(f"⚠️ Could not modify .env file: {e}")
        print("Continuing with default settings...")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    # Try virtual environment approach first
    print("🔧 Setting up virtual environment...")
    
    # Remove existing virtual environment if it exists
    import shutil
    if os.path.exists('venv'):
        print("🗑️ Removing existing virtual environment...")
        shutil.rmtree('venv')
    
    # Create virtual environment
    if not run_command("python3 -m venv venv", "Creating virtual environment"):
        return False
    
    # Upgrade pip and install setuptools first
    if not run_command("venv/bin/pip install --upgrade pip setuptools", "Upgrading pip and installing setuptools"):
        return False
    
    # Install dependencies in virtual environment
    if not run_command("venv/bin/pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def setup_database():
    """Set up the database"""
    # Run migrations using virtual environment
    if not run_command("venv/bin/python manage.py migrate", "Running database migrations"):
        return False
    
    # Create superuser using virtual environment
    print("\n👤 Creating superuser...")
    if not run_command("venv/bin/python manage.py createsuperuser --noinput --email admin@hospital.com --username admin --first_name Admin --last_name User", "Creating superuser"):
        return False
    
    # Update superuser with correct role and password
    print("🔧 Configuring superuser...")
    if not run_command("venv/bin/python manage.py shell -c \"from apps.accounts.models import User; user = User.objects.get(email='admin@hospital.com'); user.role = 'ADMIN'; user.is_staff = True; user.set_password('admin123'); user.save(); print('Superuser updated successfully')\"", "Configuring superuser"):
        return False
    
    return True

def load_sample_data():
    """Load sample data"""
    return run_command("venv/bin/python manage.py load_sample_data", "Loading sample data")

def setup_arabic():
    """Set up Arabic language support"""
    return run_command("venv/bin/python manage.py setup_arabic", "Setting up Arabic language support")

def run_tests():
    """Run tests"""
    return run_command("venv/bin/python -m pytest", "Running tests")

def check_database():
    """Check if database is accessible"""
    return run_command("venv/bin/python manage.py check --database default", "Checking database connection")

def main():
    """Main setup function"""
    print("🚀 Starting setup process...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Check database connection
    if not check_database():
        print("❌ Database connection failed")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Load sample data
    if not load_sample_data():
        print("❌ Sample data loading failed")
        sys.exit(1)
    
    # Set up Arabic language support
    if not setup_arabic():
        print("❌ Arabic language setup failed")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Start the development server: python manage.py runserver")
    print("3. Visit http://localhost:8000/api/docs/ for API documentation")
    print("4. Admin panel: http://localhost:8000/admin/")
    print("5. Login with: admin@hospital.com / admin123")
    print("\n🐳 For Docker setup:")
    print("1. docker-compose -f docker-compose.dev.yml up --build")
    print("2. Visit http://localhost:8000")

if __name__ == '__main__':
    main()

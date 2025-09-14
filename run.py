#!/usr/bin/env python3
"""
Simple run script for Hospital Management System
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🏥 Hospital Management System - Quick Start")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found!")
        print("Please run: python3 setup.py first")
        sys.exit(1)
    
    # Activate virtual environment and run server
    print("🚀 Starting development server...")
    print("📱 Access the system at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs/")
    print("🔧 Admin Panel: http://localhost:8000/admin/")
    print("👤 Login: admin@hospital.com / admin123")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the server
    try:
        subprocess.run("venv/bin/python manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

if __name__ == '__main__':
    main()

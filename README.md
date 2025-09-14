# 🏥 Django Hospital Management System

A comprehensive hospital management system built with Django, featuring Arabic language support and modern web interface.

## ✨ Features

- **Patient Management**: Complete patient records and profiles
- **Doctor Management**: Staff and doctor information management
- **Appointment Scheduling**: Book and manage appointments
- **Medical Records**: Track patient medical history
- **Reports Generation**: Generate various medical reports
- **Arabic Interface**: Full Arabic language support
- **Admin Dashboard**: Comprehensive admin interface
- **API Support**: RESTful API for mobile/web integration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahmedwmh/Django_Hospital_System.git
   cd Django_Hospital_System
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open http://localhost:8000
   - Login with your superuser credentials

## 🌐 Live Demo

**Production URL**: https://urchin-app-j2low.ondigitalocean.app/

**Default Login Credentials**:
- Username: `admin`
- Password: `admin123`

## 🛠️ Technology Stack

- **Backend**: Django 4.2.16
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **API**: Django REST Framework
- **Authentication**: JWT tokens
- **Deployment**: DigitalOcean App Platform
- **Language**: Arabic (RTL support)

## 📁 Project Structure

```
Django_Hospital_System/
├── apps/
│   ├── accounts/          # User management
│   ├── hospital/          # Hospital and staff management
│   ├── patients/          # Patient management
│   ├── reports/           # Reports generation
│   └── dashboard/         # Dashboard views
├── hospital_system/       # Main Django project
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_POSTGRESQL=False  # True for PostgreSQL, False for SQLite

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Language
LANGUAGE_CODE=ar
TIME_ZONE=Asia/Baghdad
```

## 🚀 Deployment

### DigitalOcean App Platform

1. Connect your GitHub repository to DigitalOcean App Platform
2. Set the following environment variables:
   ```
   DEBUG=False
   USE_POSTGRESQL=False
   ALLOWED_HOSTS=your-app-domain.ondigitalocean.app
   SECRET_KEY=your-production-secret-key
   ```
3. Deploy automatically from main branch

## 📱 API Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **Schema**: `/api/schema/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ahmed Mohammed**
- GitHub: [@ahmedwmh](https://github.com/ahmedwmh)

## 🙏 Acknowledgments

- Django community for the amazing framework
- DigitalOcean for hosting platform
- All contributors and testers

---

**Made with ❤️ for better healthcare management**
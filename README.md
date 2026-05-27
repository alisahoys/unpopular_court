# ⚖️ Unpopular Opinions Court

A retro-terminal courtroom where unpopular opinions go on trial. Built with Django + django-allauth.

## Features
- Post unpopular opinions that go on trial for 24 hours
- Defend or prosecute other users' opinions
- Verdict system: defended / prosecuted / hung jury
- Tag-based filtering and keyword search
- Email verification on signup
- Contrarian Score — tracks how many of your opinions were successfully defended
- Unique pixel art avatars per user

## Live Demo
https://unpopular-court.onrender.com

## Test Account
To explore the app without registering:
```
login: user
password: user12345
```

## Tech Stack
- Python 3.14
- Django 6.0
- django-allauth
- SQLite

## Setup

### 1. Clone the repo
git clone https://github.com/alisahoys/unpopular_court.git
cd unpopular_court

### 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Create a `.env` file in the project root
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

### 5. Run migrations
python manage.py migrate

### 6. Create a superuser
python manage.py createsuperuser

### 7. Configure the Site
Go to `/admin/` → Sites → change `example.com` to `127.0.0.1:8000`

### 8. Run the server
python manage.py runserver

## Running Tests
python manage.py test court

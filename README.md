# ⚖️ Unpopular Opinions Court

A retro-terminal courtroom where unpopular opinions go on trial. Built with Django.

## How it works
- Post an unpopular opinion
- Other users must write an argument (defend or prosecute) before they can read others
- After 24 hours the verdict is in
- Build your Contrarian Score by successfully defending unpopular opinions

## Tech Stack
- Python 3.14
- Django
- SQLite

## Setup
1. Clone the repo
2. Create and activate a virtual environment
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`
# readmatch 💗

**A dating app, but for readers!**

This is a Django-based project that matches you with readers who are most compatible with you by using Goodreads data and quiz responses. This is done by analyzing your reading history, genre preferences, and recency weightage to pair you accurately.

## Features:
- Upload Goodreads data and import books
- Users are matched based on genre preferences and reading patterns
- Shuffle feature allows you to find another match
- The matching algorithm uses cosine similarity and gives more weight to recently read books
- Django backend with user login, data import endpoints, and match generation logic

## How to Run:
```bash
git clone https://github.com/nayana1729/readmatch.git
cd readmatch/readmatch-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Then go to http://127.0.0.1:8000/

## Notes:
This project is still in progress! Backend is functional and tested, and frontend is in development.

# readmatch 💗

**a dating app, but for readers !**

this is a django-based project that matches you with readers who are most compatible with you. all you have to do is upload your goodreads data, complete a short quiz, and click the match button !

find a book buddy for life !!

## features:
- upload goodreads data and import books
- users are matched based on genre preferences and reading patterns
- if you are unhappy with your match, click shuffle and easily find a better reading buddy
- the matching algorithm uses cosine similarity and weights recently read books higher

## how to use:
```bash
git clone https://github.com/nayana1729/readmatch.git
cd readmatch/readmatch-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
then go to http://127.0.0.1:8000/

## notes:
this project is still in progress ! backend is working and tested (more features will be added soon :D) and frontend is in the works.

## credits:
created by me ! (https://github.com/nayana1729)
thank you to ani musunuri for the idea :)))

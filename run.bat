@echo off
set FLASK_APP=app.py
set FLASK_ENV=development
call venv\Scripts\activate
flask run
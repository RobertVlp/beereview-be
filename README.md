# How to run
* Create a new python environment with `python -m venv venv`
* Make sure the powershell instance can run commands `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Start the environment `.\venv\Scripts\activate.ps1`
* Install the required packages `pip install -r requirements.txt`
* Start the flask backend *automatically on http://localhost:5000* with `flask run`

## Prerequisites
* Python 3.x
* MongoDB Compass needs to be installed on the local machine and the database should be accessed via `mongodb://localhost:27017/beereview`

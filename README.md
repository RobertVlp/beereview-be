# How to run
python -m venv venv
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate.ps1
pip install -r requirements.txt
flask run

# Beereview backend

## How to run
Create a new python environment with `python -m venv venv` <br />
Make sure the powershell instance can run commands `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` <br />
Start the environment `.\venv\Scripts\activate.ps1` <br />
Install the required packages `pip install -r requirements.txt` <br />
Start the flask backend *automatically on http://localhost:5000* with `flask run` <br />

## Endpoints
### Creating an account and login
**/login** - `POST` {
    "username": "admin",
    "password": "admin"
} <br />
**/register** - `POST` {
    "username": "admin",
    "password": "admin"
} <br />
**/protected** - `GET` needs bearer token auth header <br />

### Fetching beers, breweries
**/beers** - `GET` with query params <br />
**/beers/categories** - `GET` <br />
**/breweries/[optional id]** `GET` with query params or id path parameter <br />

### Managing favourites beers inside the account
**/favourites** needs bearer token auth header
* `GET` json arary with beers
* `POST` {"beer_id": "28"}
* `DELETE` {"beer_id": "28"}

### Getting recommendations based on favourites beer styles
**/recommendations"" `GET` needs bearer token auth header <br />
**/chatbot"" `GET` needs bearer token auth header <br />

## Prerequisites
* .env file containing the line: `OPENAI_API_KEY="<api_key>"`
* Python 3.x
* MongoDB Compass needs to be installed on the local machine and the database should be accessed via `mongodb://localhost:27017/beereview`

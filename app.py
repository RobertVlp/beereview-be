from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
import json
from os import path

app = Flask(__name__)
base_dir = path.dirname(path.abspath(__file__))
config_file_path = path.join(base_dir, 'config.json')

with open(config_file_path) as config_file:
    app.config.update(json.load(config_file))

jwt = JWTManager(app)

client = MongoClient(app.config['MONGODB_SETTINGS']['host'])
db = client[app.config['MONGODB_SETTINGS']['host'].split('/')[-1]]
users_collection = db['users']
beers_collection = db['beers']
breweries_collection = db['breweries']


class user_schema:
    def __init__(self, username, password, fav_beers):
        self.username = username
        self.password = password
        self.fav_beers = fav_beers

    def to_json(self):
        return {
            'username': self.username,
            'password': self.password,
            'fav_beers': self.fav_beers
        }

    @staticmethod
    def from_json(json):
        return user_schema(
            json['username'],
            json['password'],
            json['fav_beers']
        )


def hash_password(password):
    hashed_password = password
    return hashed_password

@app.before_first_request
def before_first_request():
    if not users_collection.find_one({'username': 'admin'}):
        users_collection.insert_one({'username': 'admin', 'password': hash_password('admin'), 'fav_beers': []})
    
    if not beers_collection.find_one():
        add_beers()
        
    if not breweries_collection.find_one():
        add_breweries()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    if users_collection.find_one({'username': data['username']}):
        return jsonify({'message': 'Username already exists'}), 400

    users_collection.insert_one(user_schema(data['username'], hash_password(data['password']), []).to_json())

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    user = users_collection.find_one({'username': username})

    if not user or user['password'] != password:
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username, expires_delta=False)
    return jsonify({'access_token': access_token})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Welcome, {current_user}'})


@app.route('/beers', methods=['GET'])
def get_beers():
    query = {}
    for key, value in request.args.items():
        query[key] = value
        
    beers = beers_collection.find(query, {'_id': 0})
    beers_with_brewery = [{**beer, 'brewery': breweries_collection.find_one({'id': str(beer['brewery_id'])}, {'_id': 0})} for beer in beers]
    
    return jsonify(beers_with_brewery)


@app.route('/beers/categories', methods=['GET'])
def get_categories():
    categories = beers_collection.distinct('cat_name')
    categories = [{category: beers_collection.distinct('style_name', {'cat_name': category})} for category in categories]
    return jsonify(categories)

@app.route('/favourites', methods=['POST'])
@jwt_required()
def add_favourite():
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('beer_id'):
        return jsonify({'message': 'Missing beer_id'}), 400

    beer_id = data['beer_id']
    if not beers_collection.find_one({'id': str(beer_id)}):
        return jsonify({'message': 'Beer not found'}), 404 
    beer_id = str(beer_id)
    
    user = users_collection.find_one({'username': current_user})

    if beer_id in user['fav_beers']:
        return jsonify({'message': 'Beer already in favourites'}), 400

    user['fav_beers'].append(beer_id)
    users_collection.update_one({'username': current_user}, {'$set': {'fav_beers': user['fav_beers']}})

    return jsonify({'message': 'Beer added to favourites'}), 201

@app.route('/favourites', methods=['GET'])
@jwt_required()
def get_favourites():
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    fav_beers = beers_collection.find({'id': {'$in': user['fav_beers']}}, {'_id': 0})
    
    fav_beers = [{**beer, 'brewery': breweries_collection.find_one({'id': str(beer['brewery_id'])}, {'_id': 0})} for beer in fav_beers]
    return jsonify(list(fav_beers))


@app.route('/breweries', methods=['GET'])
def get_breweries():
    query = {}
    for key, value in request.args.items():
        query[key] = value

    breweries = breweries_collection.find(query, {'_id': 0})
    return jsonify(list(breweries))

@app.route('/breweries/<int:brewery_id>', methods=['GET'])
def get_brewery(brewery_id):
    brewery = breweries_collection.find_one({'id': str(brewery_id)}, {'_id': 0})
    return jsonify(brewery)

def add_beers():
    with open('beers.json', 'r', encoding='utf-8') as beers_file:
        beers = json.load(beers_file)
        beers_collection.insert_many(beers)
    
def add_breweries():
    with open('breweries.json', 'r', encoding='utf-8') as breweries_file:
        breweries = json.load(breweries_file)
        breweries_collection.insert_many(breweries)

if __name__ == '__main__':
    app.run(debug=True)
    
    

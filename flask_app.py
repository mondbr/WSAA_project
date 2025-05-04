# This is a simple Flask application that serves as a RESTful API for a database of transactions.
# this code was inspired by the server.py code by Andrew Beatty in WSAA course

# importing necessary libraries
import json
from flask import Flask, request, jsonify


# Create a Flask app
app = Flask(__name__)

# Path to the JSON database file
database = 'songs.json'

# Map url to the function
# This is the main page of the application
@app.route('/')
def home():
    return "This is a Home Page" # This is rerturing a message at the home page as a HTTP response

# Define a route for the /items endpoint
def read_db():
    try:
        with open(database, 'r') as file:
            data = json.load(file)
            return data['Songs']
    except FileNotFoundError:
        return []
    
# route for retrieving items from the database
@app.route('/items', methods=['GET'])
def get_items():
    items = read_db()
    return jsonify(items)

# running the flask app
if __name__ == "__main__":
    app.run(debug = True)

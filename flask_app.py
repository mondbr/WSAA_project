# This is a simple Flask application that serves as a RESTful API for a database of transactions.
# this code was inspired by the server.py code by Andrew Beatty in WSAA course

# importing necessary libraries
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from TransactionDAO import TransactionDAO

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'



#app = Flask(__name__, static_url_path='', static_folder='.')

# Map url to the function
# This is the main page of the application

@app.route('/')
@cross_origin()
def home():
    return "Welcome to the Personal Budget Tracker where you can manage your spending!" # This is rerturing a message at the home page as a HTTP response


@app.route('/transactions')
@cross_origin()


# http://127.0.0.1:5000/transactions

def get_all_transactions():
    results = TransactionDAO.get_all()
    return jsonify(results)



@app.route('/transactions/<int:id>')
@cross_origin()
def get_transaction_by_id(id):
    transaction = TransactionDAO.find_by_id(id)
    if transaction:
        return jsonify(transaction)
    else:
        abort(404, description="Transaction not found")


@app.route('/transactions', methods=["GET"])
@cross_origin()
def get_transactions():
    transactions = TransactionDAO.get_all()
    return jsonify(transactions)



# curl -i -H "Content-Type:application/json" -X POST -d "{\"description\":\"Salary\",\"amount\":5000.00,\"transaction_type\":\"income\"}" http://127.0.0.1:5000/transactions
@app.route('/transactions', methods=['POST'])
@cross_origin()
def create_transaction():
    if not request.json:
        abort(400)
    transaction = {
        "description": request.json['description'],
        "amount": request.json['amount'],
        "transaction_type": request.json['transaction_type'],
    }
    added_transaction = TransactionDAO.create(transaction)

    return jsonify(added_transaction), 201

# curl -i -H "Content-Type:application/json" -X PUT -d "{\"description\":\"Updated Salary\",\"amount\":6000.00,\"transaction_type\":\"income\"}" http://127.0.0.1:5000/transactions/1
@app.route('/transactions/<int:id>', methods=['PUT'])
@cross_origin()
def update_transaction(id):
    transaction = TransactionDAO.find_by_id(id)
    if not transaction:
        abort(404)

    if not request.json:
        abort(400)

    updated_transaction = {
        "description": request.json.get('description', transaction['description']),
        "amount": request.json.get('amount', transaction['amount']),
        "transaction_type": request.json.get('transaction_type', transaction['transaction_type']),
    }
    TransactionDAO.update(id, updated_transaction)
    return jsonify(updated_transaction)

# curl -i -X DELETE http://127.0.0.1:5000/transactions/1
@app.route('/transactions/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_transaction(id):
    transaction = TransactionDAO.find_by_id(id)
    if not transaction:
        abort(404)

    TransactionDAO.delete(id)
    return jsonify({"result": True})


# running the flask app
if __name__ == "__main__":
    app.run(debug = True)

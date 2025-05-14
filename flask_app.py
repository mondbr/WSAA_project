# This is a simple Flask application that serves as a RESTful API for a database of transactions.
# this code was inspired by the server.py code by Andrew Beatty in WSAA course

# importing necessary libraries
import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from TransactionDAO import TransactionDAO
# this is a module that handle currency exchange https://github.com/everapihq/freecurrencyapi-python
import freecurrencyapi

# this is to handle api key (reffered to assignment 04)
from config import config as cfg

# this is to handle downloading the data from the database
import csv # to handle csv files 
from io import StringIO # to handle string data in memory https://www.geeksforgeeks.org/stringio-module-in-python/
from flask import Response # to handle response http://flask.pocoo.org/docs/1.0/api/#flask.Response


# this is to handle api key (reffered to assignment 04)
api_key = cfg["MYAPIKEY"]

#according to the documentation  https://github.com/everapihq/freecurrencyapi-python
client = freecurrencyapi.Client(api_key)
print(client.status()) # check if the API key is valid



app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'


# added function to get exchange rate from EUR TO USD
def get_exchange_rate():
    try:
        response = client.latest() #according to the documentation  https://github.com/everapihq/freecurrencyapi-python
        if 'EUR' in response['data']:
            exchange_rate = 1 / response['data']['EUR'] # get the exchange rate from EUR to USD as USD is always 1, so divide 1 by the exchange rate of EUR
            
            return exchange_rate
        else:
            # If the response does not contain 'USD', handle it accordingly
            print("USD not found in the response")
            return None
        
    except Exception as e:
        print("Error fetching exchange rate: " + str(e))
        return None


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
    print("Results: ", results)
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

    try:
        amount = float(request.json['amount'])
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    exchange_rate = get_exchange_rate()
    if exchange_rate is None:
        return jsonify({"error": "Failed to fetch exchange rate"}), 500
    
   
    
    #limit the amounts to decimal places
    amount_in_usd = round(amount * exchange_rate, 2) # Convert amount to USD using the exchange rate
    exchange_rate = round(exchange_rate, 4)
    
    transaction = {
        "description": request.json['description'],
        "amount": amount,
        "transaction_type": request.json['transaction_type'],
        "amount_in_usd": amount_in_usd, 
        "exchange_rate": exchange_rate # Store the exchange rate used for conversion
        
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

    new_amount = request.json.get('amount', transaction['amount'])
    new_description = request.json.get('description', transaction['description'])
    new_transaction_type = request.json.get('transaction_type', transaction['transaction_type'])
    get_exchange_rate = float(transaction['exchange_rate'])
    new_amount_in_usd = round(new_amount * get_exchange_rate, 2) # Convert amount to USD using the exchange rate

    updated_transaction = {
        "description": new_description,
        "amount": new_amount,   
        "transaction_type": new_transaction_type,
        "amount_in_usd": new_amount_in_usd,  # Update the amount in USD
        "exchange_rate": get_exchange_rate  # Keep the same exchange rate
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

# api key 
@app.route('/get-api-key', methods=['GET'])
@cross_origin()
def get_api_key():
    api_key = cfg["MYAPIKEY"]
    # Return the API key as a JSON response
    return jsonify({"api_key": api_key})


# download the data from the database
@app.route('/download_transactions', methods=['GET'])
@cross_origin()
def download_transactions():
    # Fetch all transactions from the MySQL database using TransactionDAO
    transactions = TransactionDAO.get_all()
    
    # Create a CSV output in memory http://flask.pocoo.org/docs/1.0/api/#flask.Response
    si = StringIO() # https://stackoverflow.com/questions/56804363/sending-a-dataframe-using-flask-route-to-be-saved-as-csv
    writer = csv.writer(si) # https://stackoverflow.com/questions/13120127/how-can-i-use-io-stringio-with-the-csv-module
    
    # Write the CSV header (column names)
    writer.writerow(['ID', 'Description', 'Amount', 'Transaction Type', 'Amount in USD', 'Exchange Rate'])
    
    # Write each transaction's data
    for transaction in transactions:
        writer.writerow([transaction['id'], transaction['description'], transaction['amount'], 
                         transaction['transaction_type'], transaction['amount_in_usd'], transaction['exchange_rate']])
    
    # Prepare the CSV for download
    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="transactions.csv")
    
    return response



# running the flask app
if __name__ == "__main__":
    app.run(debug = True)

from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# CoinGecko API endpoint for Bitcoin price
API_URL = "https://api.coingecko.com/api/v3/simple/price"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_price')
def get_price():
    try:
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd,cny'
        }
        response = requests.get(API_URL, params=params)
        data = response.json()
        
        # Format the data
        price_data = {
            'usd': data['bitcoin']['usd'],
            'cny': data['bitcoin']['cny'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(price_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

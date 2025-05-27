from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, RegistrationForm, LoginForm
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CoinGecko API endpoint for Bitcoin price
API_URL = "https://api.coingecko.com/api/v3/simple/price"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_bitcoin_price():
    try:
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd,cny'
        }
        response = requests.get(API_URL, params=params)
        data = response.json()
        return {
            'usd': data['bitcoin']['usd'],
            'cny': data['bitcoin']['cny']
        }
    except Exception as e:
        return None

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    bitcoin_price = get_bitcoin_price()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录。')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, bitcoin_price=bitcoin_price)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    bitcoin_price = get_bitcoin_price()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('用户名或密码错误')
    return render_template('login.html', form=form, bitcoin_price=bitcoin_price)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_price')
@login_required
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)

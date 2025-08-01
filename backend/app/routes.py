from flask import Blueprint, request, jsonify
import os
from flask_cors import CORS
from flask import Blueprint, request, jsonify, session, make_response, current_app
from app.models import Helpdesk, User, Stock
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import jwt
import datetime
import time
import yfinance as yf
import numpy as np
import tensorflow as tf
import joblib
from app.methods_for_training_model import fetch_stock_data, create_features


api_bp = Blueprint('api', __name__)
base_dir = os.path.dirname(os.path.abspath(__file__))
CORS(api_bp)


@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return make_response(jsonify({'message': 'Missing required fields'}), 400)

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)).first()
    if existing_user:
        return make_response(jsonify({'message': 'Username or email already exists'}), 409)

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)

    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            db.session.commit()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                db.session.rollback()
                time.sleep(retry_delay)
            else:
                raise e

    return make_response(jsonify({'message': 'User registered successfully'}), 201)


@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(jsonify({'message': 'Missing required fields'}), 400)

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'])

        return jsonify({'token': token, 'user': {'email': user.email, 'username': user.username}}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@api_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'User logged out successfully'})


@api_bp.route('/helpdesk', methods=['POST'])
def helpdesk():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    message = data.get('message')

    if (data.get('user_id') is not None):
        user_id = data.get('user_id')
    else:
        query_result = db.session.query(
            User.id).filter(User.email == email).first()
        user_id = query_result[0] if query_result else None

    new_helpdesk = Helpdesk(firstname=firstname, lastname=lastname,
                            email=email, message=message, user_id=user_id)
    print(new_helpdesk)
    db.session.add(new_helpdesk)

    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            db.session.commit()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                db.session.rollback()
                time.sleep(retry_delay)
            else:
                raise e

    return make_response(jsonify({'message': 'Helpdesk ticket created successfully'}), 201)


@api_bp.route('/helpdesk/<email>', methods=['GET'])
def get_helpdesk_tickets(email):
    helpdesk_tickets = Helpdesk.query.filter_by(email=email).all()
    tickets = [{'firstname': ticket.firstname, 'lastname': ticket.lastname,
                'email': ticket.email, 'message': ticket.message} for ticket in helpdesk_tickets]
    return jsonify(tickets)


@api_bp.route('/stocks', methods=['GET'])
def get_available_stocks():
    stocks = Stock.query.all()
    print(stocks)
    stock_list = [{'code': stock.symbol, 'name': stock.name}
                  for stock in stocks]
    return jsonify(stock_list)


@api_bp.route('/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    # Fetch historical stock data using yfinance
    stock_data = yf.download(symbol, start='2022-01-01',
                             end=datetime.datetime.now().strftime('%Y-%m-%d'))

    # Extract the closing prices and dates
    closing_prices = stock_data['Close'].values
    dates = stock_data.index.strftime('%Y-%m-%d').tolist()

    # Prepare the response data
    data = {
        'symbol': symbol,
        'prices': closing_prices.tolist(),
        'labels': dates
    }

    return jsonify(data)


@api_bp.route('/stocks/<symbol>/predict', methods=['GET'])
def predict_stock(symbol):
    model = tf.keras.models.load_model(
        'app/stock_prediction_tuned_model.keras')
    scaler = joblib.load('app/tuned_scaler.pkl')

    # Fetch data for the symbol
    data = fetch_stock_data(symbol, period='2y')  # Fetch 2 years data
    features = create_features(data)
    scaled_features = scaler.transform(features.values)

    # Historical data for plotting
    historical_close_prices = data['Close'][-720:].tolist()
    # Assuming data has a DateTimeIndex
    historical_dates = data.index[-720:].strftime('%Y-%m-%d').tolist()

    # Prepare the initial input for prediction (last 60 days)
    input_features = np.array([scaled_features[-60:]])

    predictions = []
    for _ in range(7):  # Predict for 7 days
        daily_prediction = model.predict(input_features)
        predictions.append(daily_prediction[0, 0])

        next_input_features = np.roll(input_features, -1, axis=1)
        next_day_features = scaled_features[-1].copy()
        # Assumed index 3 is the target feature
        next_day_features[3] = daily_prediction[0, 0]
        next_input_features[0, -1, :] = next_day_features
        input_features = next_input_features

    predictions_extended = np.tile(scaled_features[-1], (7, 1))
    predictions_extended[:, 3] = predictions
    inverse_predictions = scaler.inverse_transform(predictions_extended)[:, 3]

    # Generate prediction dates
    last_date = datetime.datetime.strptime(historical_dates[-1], '%Y-%m-%d')
    predicted_dates = [(last_date + datetime.timedelta(days=i)
                        ).strftime('%Y-%m-%d') for i in range(1, 8)]

    return jsonify({
        'symbol': symbol,
        'historical_prices': historical_close_prices,
        'historical_dates': historical_dates,
        'predicted_prices': inverse_predictions.tolist(),
        'predicted_dates': predicted_dates
    })

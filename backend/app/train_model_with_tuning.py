# train_model_with_tuning.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from stock_lookup import stock_lookup_training
import joblib
from kerastuner.tuners import RandomSearch

# Step 1: Fetch Data from Multiple Stocks


def fetch_stock_data(ticker, period='10y'):  # Increase data period
    stock = yf.Ticker(ticker)
    return stock.history(period=period)


def create_features(df):
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['RSI'] = compute_rsi(df['Close'])
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean(
    ) - df['Close'].ewm(span=26, adjust=False).mean()
    df['Volume'] = df['Volume']
    df['Momentum'] = df['Close'] - df['Close'].shift(4)
    df['Stochastic_K'] = 100 * (df['Close'] - df['Low'].rolling(window=14).min()) / (
        df['High'].rolling(window=14).max() - df['Low'].rolling(window=14).min())
    df = df.dropna()
    return df


def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# Collect data for all tickers
all_data = []

for ticker in stock_lookup_training:
    data = fetch_stock_data(ticker)
    data = create_features(data)
    data['Ticker'] = ticker  # Add a column for the ticker
    all_data.append(data)

all_data = pd.concat(all_data)

# Step 2: Feature Engineering
# (Already done in create_features function)

# Step 3: Data Preparation
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(all_data.drop(columns=['Ticker']).values)

# Save the scaler for later use
joblib.dump(scaler, 'tuned_scaler_2nd.pkl')

x_train = []
y_train = []

for i in range(60, len(scaled_data)):
    x_train.append(scaled_data[i-60:i])
    y_train.append(scaled_data[i, 3])  # Assuming 'Close' is at index 3

x_train, y_train = np.array(x_train), np.array(y_train)

# Define the model for hyperparameter tuning


def build_model(hp):
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.LSTM(units=128, return_sequences=True,
              input_shape=(x_train.shape[1], x_train.shape[2])))
    model.add(tf.keras.layers.LSTM(units=128, return_sequences=False))
    model.add(tf.keras.layers.Dense(units=128))
    model.add(tf.keras.layers.Dense(1))

    model.compile(optimizer=tf.keras.optimizers.Adam(hp.Choice(
        'learning_rate', values=[1e-2, 1e-3])), loss='mean_squared_error')

    return model


# Create the tuner
tuner = RandomSearch(
    build_model,
    objective='val_loss',
    # max_trials=3,  # Only 3 trials for the 3 different learning rates
    max_trials=2,  # Only 2 trials for the best learning rates
    # executions_per_trial=2,  # Two execution2 per trial
    executions_per_trial=1,  # Set to 1 to reduce training time for 2nd tuning
    directory='tuning_training_models',
    project_name='stock_prediction_2nd_tuning')

# Split the data into training and validation sets
split = int(0.8 * len(x_train))
x_train_split, x_val_split = x_train[:split], x_train[split:]
y_train_split, y_val_split = y_train[:split], y_train[split:]

# Perform hyperparameter tuning
tuner.search(x_train_split, y_train_split, epochs=25,
             validation_data=(x_val_split, y_val_split))

# Get the best model
best_model = tuner.get_best_models(num_models=1)[0]
best_model.summary()

# Save the best model
best_model.save('stock_prediction_tuned_model_2nd.keras')

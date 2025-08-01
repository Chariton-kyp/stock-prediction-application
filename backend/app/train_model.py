# train_model.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from stock_lookup import stock_lookup_training
import joblib

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
joblib.dump(scaler, 'path_to_your_scaler.pkl')

x_train = []
y_train = []

for i in range(60, len(scaled_data)):
    x_train.append(scaled_data[i-60:i])
    y_train.append(scaled_data[i, 3])  # Assuming 'Close' is at index 3

x_train, y_train = np.array(x_train), np.array(y_train)

# Step 4: Model Training


def build_model(input_shape):
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.LSTM(
        50, return_sequences=True, input_shape=input_shape))
    model.add(tf.keras.layers.LSTM(50, return_sequences=False))
    model.add(tf.keras.layers.Dense(25))
    model.add(tf.keras.layers.Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


model = build_model((x_train.shape[1], x_train.shape[2]))

# Early stopping callback
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='loss', patience=5, restore_best_weights=True)

# Train the model
model.fit(x_train, y_train, batch_size=32,
          epochs=25, callbacks=[early_stopping])

# Step 5: Save the Model
model.save('path_to_your_model.keras')

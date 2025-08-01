from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib


def fetch_stock_data(ticker, period='5y'):
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


# Load the scaler
scaler = joblib.load('tuned_scaler.pkl')

# Load the model
model = tf.keras.models.load_model('stock_prediction_tuned_model.keras')

# Prepare test data
# Example with 'MYTIL.AT', use different stock for complete test
test_data = fetch_stock_data('MYTIL.AT', period='1y')
test_data = create_features(test_data)

# Scale the data
scaled_test_data = scaler.transform(test_data.values)

x_test = []
y_test = []

for i in range(60, len(scaled_test_data)):
    x_test.append(scaled_test_data[i-60:i])
    y_test.append(scaled_test_data[i, 3])  # Assuming 'Close' is at index 3

x_test = np.array(x_test)
y_test = np.array(y_test)

# Make predictions
predictions = model.predict(x_test)

# Create a placeholder for inverse transform
predictions_extended = np.zeros(
    (predictions.shape[0], scaled_test_data.shape[1]))
# Assuming 'Close' is at index 3
predictions_extended[:, 3] = predictions[:, 0]

# Inverse transform the predictions
predictions = scaler.inverse_transform(predictions_extended)[:, 3]

# Plot predictions vs actual values
plt.figure(figsize=(14, 5))
plt.plot(test_data.index[60:], predictions,
         color='red', label='Predicted Prices')
plt.plot(test_data.index[60:], test_data['Close']
         [60:], color='blue', label='Actual Prices')
plt.title('Stock Price Predictions vs Actual Prices')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")

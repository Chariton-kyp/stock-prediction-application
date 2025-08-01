import yfinance as yf


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

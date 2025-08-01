import yfinance as yf
from app import db
from app.models import Stock
from app.stock_lookup import stock_lookup


def fetch_and_store_stocks(app):
    with app.app_context():
        # Fetch all existing stocks from the database once
        existing_stocks = {stock.symbol for stock in Stock.query.all()}

        # Iterate through the stock_lookup list
        for symbol in stock_lookup:
            if symbol not in existing_stocks:
                stock_info = yf.Ticker(symbol).info
                stock_name = stock_info.get('longName', symbol)
                stock = Stock(symbol=symbol, name=stock_name)
                db.session.add(stock)

        db.session.commit()

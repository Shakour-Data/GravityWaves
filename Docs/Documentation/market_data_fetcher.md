# market_data_fetcher.py Documentation

## Overview
The `market_data_fetcher.py` module provides a unified interface for fetching historical market data from multiple sources, including Yahoo Finance and the Tehran Stock Exchange (TSE). It defines an abstract `DataSource` base class and concrete implementations for each data source. The `MarketDataFetcher` class manages data source selection, data fetching with retries, and data cleaning.

---

## Classes

### DataSource (Abstract Base Class)
Defines the interface for market data sources. Requires implementation of the `fetch_data` method to retrieve historical OHLCV data for a given ticker and date range.

### YahooFinanceDataSource
Fetches historical market data from Yahoo Finance using the `yfinance` library. Handles data cleaning, column normalization, and logging.

### TSEDataSource
Fetches historical market data from the Tehran Stock Exchange using the `finpy_tse` library. Converts Gregorian dates to Shamsi (Jalali) dates, handles ticker symbol mapping, and normalizes data.

### MarketDataFetcher
Manages fetching market data from the selected data source (`yahoo` or `tse`). Supports retries, date range calculation, data cleaning, and logging.

---

## Functions

### load_market_data
Wrapper function to instantiate `MarketDataFetcher` and fetch market data for a given ticker, data source, timeframe, and candle count.

---

## Usage Example

```python
from datetime import datetime
from app.services.market_data_fetcher import load_market_data

# Fetch 100 daily candles for AAPL from Yahoo Finance
data = load_market_data("AAPL", "yahoo", "1d", 100)
print(data.head())
```

---

## Diagrams

- **Class Diagram:** Shows DataSource, YahooFinanceDataSource, TSEDataSource, and MarketDataFetcher relationships.
- **Sequence Diagram:** Illustrates the flow of data fetching, retries, and data cleaning.

---

This documentation provides a detailed understanding of the market data fetching system and its usage within the application.

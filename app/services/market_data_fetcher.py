import pandas as pd
import yfinance as yf
import finpy_tse as tse
import jdatetime
import re
from datetime import datetime, timedelta
from typing import Optional
from abc import ABC, abstractmethod

from app.services.log_manager import LogManager


class DataSource(ABC):
    """Abstract base class for market data sources."""

    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager

    @abstractmethod
    def fetch_data(self, ticker: str, start_date: datetime, end_date: datetime, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Fetches historical market data for a given ticker.

        Args:
            ticker (str): The stock ticker symbol.
            start_date (datetime): The start date for data fetching.
            end_date (datetime): The end date for data fetching.
            timeframe (str): The data aggregation period (e.g., "1d", "1h").

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing historical OHLCV data,
                                    or None if data fetching fails.
        """
        pass


class YahooFinanceDataSource(DataSource):
    """Data source for fetching data from Yahoo Finance."""

    def __init__(self, log_manager: LogManager = None):
        super().__init__(log_manager or LogManager())

    def fetch_data(self, ticker: str, start_date: datetime, end_date: datetime, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Fetches historical market data from Yahoo Finance.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL").
            start_date (datetime): The start date for data fetching.
            end_date (datetime): The end date for data fetching.
            timeframe (str): The data aggregation period (e.g., "1d", "1wk", "1mo").

        Returns:
            Optional[pd.DataFrame]: A DataFrame with columns ['open', 'high', 'low', 'close', 'volume'],
                                    or None if data fetching fails.
        """
        self.log_manager.info(
            f"Fetching YahooFinance data for {ticker} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        try:
            # yfinance expects end_date to be exclusive, so add one day
            data = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                interval=str(timeframe), # Explicitly cast to string to prevent 'tuple' object error
                progress=False
            )
            
            # Check if the returned object is None or not a DataFrame
            if data is None:
                self.log_manager.error(f"yf.download returned None for {ticker}. No data received.")
                return None
            
            if not isinstance(data, pd.DataFrame):
                self.log_manager.error(f"yf.download did not return a DataFrame for {ticker}. Received type: {type(data)}. Data: {data}")
                return None

            if data.empty:
                self.log_manager.warning(f"Empty data received from Yahoo Finance for {ticker}")
                return None
                
            data.index.name = 'Date'
            
            # --- START OF MODIFICATION ---
            # If columns are a MultiIndex, flatten them to the first level
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                self.log_manager.info(f"Flattened MultiIndex columns for {ticker}.")
            
            # Convert columns to string type if they are not already, then lowercase
            # This handles cases where column names might be non-string types
            new_columns = []
            for col in data.columns:
                if isinstance(col, str):
                    new_columns.append(col.lower())
                else:
                    # If a column name is not a string, convert it to string before lowercasing
                    self.log_manager.warning(f"Non-string column name found: {col} (type: {type(col)}). Converting to string.")
                    new_columns.append(str(col).lower())
            data.columns = new_columns
            # --- END OF MODIFICATION ---
            
            # Ensure required columns exist
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_cols):
                self.log_manager.error(f"Missing required columns in Yahoo Finance data for {ticker}. Found: {data.columns.tolist()}")
                return None

            return data[required_cols]
            
        except Exception as e:
            self.log_manager.error(
                f"YahooFinance data fetch failed for {ticker}: {str(e)}",
                exc_info=True
            )
            return None


class TSEDataSource(DataSource):
    """Data source for fetching data from Tehran Stock Exchange (TSE) using finpy_tse."""

    def __init__(self, log_manager: LogManager = None):
        super().__init__(log_manager or LogManager())
        self.symbol_map = {
            "foolad": "فولاد",
            "foulad": "فولاد",
            # Add more mappings as needed
        }

    def _convert_ticker(self, ticker: str) -> str:
        """Convert common English ticker names to Persian equivalents."""
        return self.symbol_map.get(ticker.lower(), ticker)

    def fetch_data(self, ticker: str, start_date: datetime, end_date: datetime, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Fetches historical market data from TSE.

        Args:
            ticker (str): The stock ticker symbol (e.g., "فولاد").
            start_date (datetime): The start date for data fetching (Gregorian).
            end_date (datetime): The end date for data fetching (Gregorian).
            timeframe (str): The data aggregation period (finpy_tse primarily supports daily data).

        Returns:
            Optional[pd.DataFrame]: A DataFrame with columns ['open', 'high', 'low', 'close', 'volume'],
                                    or None if data fetching fails.
        """
        ticker = self._convert_ticker(ticker)
        self.log_manager.info(
            f"Fetching TSE data for {ticker} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        
        try:
            # Convert Gregorian dates to Shamsi (Jalali) dates
            start_date_shamsi = jdatetime.date.fromgregorian(date=start_date)
            end_date_shamsi = jdatetime.date.fromgregorian(date=end_date)
            
            self.log_manager.info(
                f"Converted to Shamsi dates - Start: {start_date_shamsi.strftime('%Y-%m-%d')}, "
                f"End: {end_date_shamsi.strftime('%Y-%m-%d')}"
            )

            # Try with double_date=True first, then fallback if not supported
            try:
                data = tse.Get_Price_History(
                    stock=ticker,
                    start_date=start_date_shamsi.strftime('%Y-%m-%d'),
                    end_date=end_date_shamsi.strftime('%Y-%m-%d'),
                    ignore_date=False,
                    adjust_price=True,
                    show_weekday=False,
                    double_date=True
                )
                self.log_manager.info("Fetched TSE data with double_date=True")
            except TypeError:
                self.log_manager.warning("double_date parameter not supported, retrying without it")
                data = tse.Get_Price_History(
                    stock=ticker,
                    start_date=start_date_shamsi.strftime('%Y-%m-%d'),
                    end_date=end_date_shamsi.strftime('%Y-%m-%d'),
                    ignore_date=False,
                    adjust_price=True,
                    show_weekday=False
                )

            if data is None or data.empty:
                self.log_manager.warning(f"Empty or None data received from TSE for {ticker}")
                return None

            # Handle date index conversion
            if 'Date' in data.columns:  # Gregorian date column available
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
            elif data.index.name == 'J-Date':  # Shamsi date index
                gregorian_dates = [
                    jdatetime.date.strptime(d, '%Y-%m-%d').togregorian() 
                    for d in data.index
                ]
                data.index = pd.to_datetime(gregorian_dates)
            else:
                self.log_manager.error("No valid date column/index found in TSE data")
                return None

            data.index.name = 'Date'

            # Standardize column names and select OHLCV columns
            column_mapping = {
                'open': ['Open', 'Open Adj'],
                'high': ['High', 'High Adj'],
                'low': ['Low', 'Low Adj'],
                'close': ['Close', 'Close Adj', 'Final'],
                'volume': ['Volume']
            }

            selected_columns = {}
            for standard_name, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in data.columns:
                        selected_columns[standard_name] = name
                        break
                else:
                    self.log_manager.warning(f"No {standard_name} column found in TSE data")
                    return None

            data = data[list(selected_columns.values())]
            data.columns = selected_columns.keys()

            return data

        except Exception as e:
            self.log_manager.error(
                f"TSE data fetch failed for {ticker}: {str(e)}",
                exc_info=True
            )
            return None


class MarketDataFetcher:
    """
    Unified market data fetcher that handles both international (Yahoo Finance) 
    and Iranian (TSE) markets.
    """

    def __init__(
        self,
        ticker: str,
        candle_count: int,
        log_manager: LogManager,
        timeframe: str = "1d",
        data_source: str = "auto",  # Modified: data_source is now a required string
        target_date: Optional[datetime] = None,
        cache_manager=None
    ):
        """
        Initializes the MarketDataFetcher.

        Args:
            ticker (str): The stock ticker symbol.
            candle_count (int): The number of historical candles to fetch.
            log_manager (LogManager): An instance of LogManager for logging.
            timeframe (str): The data aggregation period (e.g., "1d").
            data_source (str):  Explicitly specify 'yahoo' or 'tse'.  # Modified
                                 Must be provided by the user.
            target_date (Optional[datetime]): The end date for fetching data.
                                              If None, current date is used.
            cache_manager: Optional cache manager for caching data.
        """
        self.ticker = ticker
        self.candle_count = candle_count
        self.log_manager = log_manager
        self.timeframe = timeframe
        self.data_source_name = data_source  # Keep the name for clarity
        self.target_date = target_date if target_date else datetime.now()
        self.cache_manager = cache_manager

        self.data_source = self._select_data_source()
        self.log_manager.info(
            f"MarketDataFetcher initialized for {self.ticker}",
            timeframe=timeframe,
            candle_count=candle_count,
            data_source=data_source
        )

    def _select_data_source(self) -> DataSource:
        """Select data source based on the provided data_source parameter."""

        if self.data_source_name.lower() == "yahoo":
            return YahooFinanceDataSource(self.log_manager)
        elif self.data_source_name.lower() == "tse":
            return TSEDataSource(self.log_manager)
        else:
            raise ValueError(f"Invalid data source: {self.data_source_name}. Must be 'yahoo' or 'tse'.")

    def fetch_data(self) -> Optional[pd.DataFrame]:
        """
        Fetches market data using the selected data source.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing historical OHLCV data,
                                    or None if data fetching fails after retries.
        """
        max_attempts = 3
        days_needed = self.candle_count * 2  # Fetch extra to account for weekends/holidays
        start_date = self.target_date - timedelta(days=days_needed)
        end_date = self.target_date + timedelta(days=1)  # Include target date

        self.log_manager.info(
            f"MarketDataFetcher.fetch_data called with target_date={self.target_date.strftime('%Y-%m-%d')}, "
            f"candle_count={self.candle_count}, timeframe={self.timeframe}, "
            f"calculated start_date={start_date.strftime('%Y-%m-%d')}, end_date={end_date.strftime('%Y-%m-%d')}"
        )

        if start_date >= end_date:
            self.log_manager.error(
                f"Invalid date range: start_date {start_date} is not before end_date {end_date}."
            )
            return None

        for attempt in range(1, max_attempts + 1):
            self.log_manager.info(
                f"Attempt {attempt}/{max_attempts}: Fetching {self.ticker} data "
                f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            )
            
            try:
                data = self.data_source.fetch_data(
                    self.ticker,
                    start_date=start_date,
                    end_date=end_date,
                    timeframe=self.timeframe
                )

                if data is None or data.empty:
                    self.log_manager.warning(
                        f"Empty data received on attempt {attempt}/{max_attempts}"
                    )
                    continue

                # Clean and prepare the data
                data = data.sort_index()
                data = data[~data.index.duplicated(keep='first')]
                
                # Return only the requested number of candles
                result = data.tail(self.candle_count)
                self.log_manager.info(
                    f"Successfully fetched {len(result)} candles for {self.ticker}"
                )
                if len(result) < self.candle_count:
                    self.log_manager.warning(
                        f"Fetched fewer candles ({len(result)}) than requested ({self.candle_count}) for {self.ticker}."
                    )
                return result

            except Exception as e:
                self.log_manager.error(
                    f"Error fetching data on attempt {attempt}/{max_attempts}: {str(e)}",
                    exc_info=True
                )

        self.log_manager.error(
            f"Failed to fetch data for {self.ticker} after {max_attempts} attempts"
        )
        return None

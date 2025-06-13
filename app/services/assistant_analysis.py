import re
from app.services.market_data_fetcher import load_market_data
import pandas as pd
import io
import base64

def analyze_message_with_price_history_preserved(message: str) -> dict:
    """
    Preserved Price History implementation for future use.
    """
    if not message:
        return {"reply": "Please enter a message to analyze."}

    message_lower = message.lower()

    # Handle price query: "price for AAPL"
    match_price = re.search(r'price for (\w+)', message_lower)
    if match_price:
        ticker = match_price.group(1).upper()
        try:
            df = load_market_data(ticker, 'yahoo', '1d', 1)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            latest_close = df['close'].iloc[-1]
            return {"reply": f"The latest closing price for {ticker} is ${latest_close:.2f}."}
        except Exception as e:
            return {"reply": f"Error fetching market data for {ticker}: {str(e)}"}

    # Handle price history query: "price history for AAPL 30"
    match_history = re.search(r'price history for (\w+)(?: (\d+))?', message_lower)
    if match_history:
        ticker = match_history.group(1).upper()
        candle_count = int(match_history.group(2)) if match_history.group(2) else 30
        try:
            df = load_market_data(ticker, 'yahoo', '1d', candle_count)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            # Format table as HTML
            df_display = df.copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d')
            df_display = df_display.reset_index()
            html_table = df_display.to_html(index=False, classes='price-history-table', border=1)

            # Check for export request: "export csv" or "export excel"
            if 'export csv' in message_lower or 'export excel' in message_lower:
                output = io.BytesIO()
                if 'csv' in message_lower:
                    df_display.to_csv(output, index=False)
                    mime_type = 'text/csv'
                    file_ext = 'csv'
                else:
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_display.to_excel(writer, index=False, sheet_name='PriceHistory')
                    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    file_ext = 'xlsx'
                output.seek(0)
                b64_data = base64.b64encode(output.read()).decode()
                file_name = f"{ticker}_price_history.{file_ext}"
                file_link = f'<a href="data:{mime_type};base64,{b64_data}" download="{file_name}">Download {file_name}</a>'
                return {"reply_html": html_table + '<br/>' + file_link}

            return {"reply_html": html_table}
        except Exception as e:
            return {"reply": f"Error fetching price history for {ticker}: {str(e)}"}

    # If message is just a ticker symbol (e.g., "AAPL"), return price history table for default 30 candles
    if re.fullmatch(r'[A-Za-z]{1,5}', message.strip()):
        ticker = message.strip().upper()
        try:
            df = load_market_data(ticker, 'yahoo', '1d', 30)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            df_display = df.copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d')
            df_display = df_display.reset_index()
            html_table = df_display.to_html(index=False, classes='price-history-table', border=1)
            return {"reply_html": html_table}
        except Exception as e:
            return {"reply": f"Error fetching price history for {ticker}: {str(e)}"}

    return {"reply": "Sorry, I can only provide the latest price or price history for a ticker. Try 'Get price for AAPL' or 'Price history for AAPL 30'."}

def analyze_message(message: str) -> dict:
    """
    Analyze the user message and return a chatbot reply.
    This implementation attempts to parse simple commands related to market data,
    including price queries and price history.
    Returns a dict with keys 'reply' (text) and optionally 'reply_html' or 'file' (base64).
    """
    if not message:
        return {"reply": "Please enter a message to analyze."}

    message_lower = message.lower()

    # Handle price query: "price for AAPL"
    match_price = re.search(r'price for (\w+)', message_lower)
    if match_price:
        ticker = match_price.group(1).upper()
        try:
            df = load_market_data(ticker, 'yahoo', '1d', 1)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            latest_close = df['close'].iloc[-1]
            return {"reply": f"The latest closing price for {ticker} is ${latest_close:.2f}."}
        except Exception as e:
            return {"reply": f"Error fetching market data for {ticker}: {str(e)}"}

    # Handle price history query: "price history for AAPL 30"
    match_history = re.search(r'price history for (\w+)(?: (\d+))?', message_lower)
    if match_history:
        ticker = match_history.group(1).upper()
        candle_count = int(match_history.group(2)) if match_history.group(2) else 30
        try:
            df = load_market_data(ticker, 'yahoo', '1d', candle_count)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            # Format table as HTML
            df_display = df.copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d')
            df_display = df_display.reset_index()
            html_table = df_display.to_html(index=False, classes='price-history-table', border=1)

            # Check for export request: "export csv" or "export excel"
            if 'export csv' in message_lower or 'export excel' in message_lower:
                output = io.BytesIO()
                if 'csv' in message_lower:
                    df_display.to_csv(output, index=False)
                    mime_type = 'text/csv'
                    file_ext = 'csv'
                else:
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_display.to_excel(writer, index=False, sheet_name='PriceHistory')
                    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    file_ext = 'xlsx'
                output.seek(0)
                b64_data = base64.b64encode(output.read()).decode()
                file_name = f"{ticker}_price_history.{file_ext}"
                file_link = f'<a href="data:{mime_type};base64,{b64_data}" download="{file_name}">Download {file_name}</a>'
                return {"reply_html": html_table + '<br/>' + file_link}

            return {"reply_html": html_table}
        except Exception as e:
            return {"reply": f"Error fetching price history for {ticker}: {str(e)}"}

    # If message is just a ticker symbol (e.g., "AAPL"), return price history table for default 30 candles
    if re.fullmatch(r'[A-Za-z]{1,5}', message.strip()):
        ticker = message.strip().upper()
        try:
            df = load_market_data(ticker, 'yahoo', '1d', 30)
            if df.empty:
                return {"reply": f"No market data found for ticker {ticker}."}
            df_display = df.copy()
            df_display.index = df_display.index.strftime('%Y-%m-%d')
            df_display = df_display.reset_index()
            html_table = df_display.to_html(index=False, classes='price-history-table', border=1)
            return {"reply_html": html_table}
        except Exception as e:
            return {"reply": f"Error fetching price history for {ticker}: {str(e)}"}

    return {"reply": "Sorry, I can only provide the latest price or price history for a ticker. Try 'Get price for AAPL' or 'Price history for AAPL 30'."}

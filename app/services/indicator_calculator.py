
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, CCIIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice, MFIIndicator, AccDistIndexIndicator, acc_dist_index
from ta.others import CumulativeReturnIndicator
from app.services.log_manager import LogManager
from typing import Dict, Any, Optional, Union, Callable, List
from collections import defaultdict # Import defaultdict

class IndicatorCalculator:
    """
    Class to calculate various technical indicators for market data.

    This class encapsulates the logic for computing a set of common
    technical analysis indicators using the 'ta' library and custom calculations.
    It integrates with a LogManager for detailed logging of operations and errors.
    """
    def __init__(self, log_manager: LogManager = None):
        """
        Initializes the IndicatorCalculator.
        It no longer takes market_data at initialization, as it will be passed
        dynamically to calculation methods.

        Args:
            log_manager (LogManager, optional): An instance of LogManager for logging.
                                                If None, a default LogManager will be created.
        """
        self.log_manager = log_manager or LogManager()
        self.log_manager.info("IndicatorCalculator initialized")

    def _calculate_single_indicator(self, data: pd.DataFrame, indicator_type: str, params: Dict[str, Any]) -> Optional[Union[pd.Series, pd.DataFrame]]:
        """
        Calculates a single technical indicator based on its type and parameters for a given DataFrame.
        This method is updated to handle parameters that are lists, calculating multiple instances
        of the same indicator with different parameter values.

        Args:
            data (pd.DataFrame): The DataFrame containing market data (close, high, low, volume).
            indicator_type (str): The type of indicator to calculate (e.g., 'SMA', 'RSI', 'MACD').
            params (Dict[str, Any]): A dictionary of parameters specific to the indicator.
                                      Values can be single numbers or lists of numbers.

        Returns:
            Optional[Union[pd.Series, pd.DataFrame]]: The calculated indicator(s) as a Series or DataFrame,
                                                      or None if calculation fails.
        """
        if data.empty:
            self.log_manager.warning(f"Input data is empty for {indicator_type} calculation. Skipping.")
            return None

        # Ensure required columns exist in the input data
        required_cols = ['close', 'high', 'low', 'volume']
        if indicator_type == 'VWAP' and 'open' not in data.columns:
            required_cols.append('open')

        if not all(col in data.columns for col in required_cols):
            self.log_manager.error(f"Missing required columns ({required_cols}) in data for {indicator_type} calculation.")
            return None

        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']
        open_price = data['open'] if 'open' in data.columns else None

        results_df = pd.DataFrame(index=data.index)

        try:
            if indicator_type == 'SMA':
                windows = params.get('window', [14]) # Default to list for iteration
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for SMA: {window}. Skipping.")
                        continue
                    results_df[f'SMA_{window}'] = SMAIndicator(close=close, window=int(window)).sma_indicator()

            elif indicator_type == 'EMA':
                windows = params.get('window', [12])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for EMA: {window}. Skipping.")
                        continue
                    results_df[f'EMA_{window}'] = EMAIndicator(close=close, window=int(window)).ema_indicator()

            elif indicator_type == 'RSI':
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for RSI: {window}. Skipping.")
                        continue
                    results_df[f'RSI_{window}'] = RSIIndicator(close=close, window=int(window)).rsi()

            elif indicator_type == 'MACD':
                window_fasts = params.get('window_fast', [12])
                window_slows = params.get('window_slow', [26])
                window_signs = params.get('window_sign', [9])

                window_fasts = [window_fasts] if not isinstance(window_fasts, list) else window_fasts
                window_slows = [window_slows] if not isinstance(window_slows, list) else window_slows
                window_signs = [window_signs] if not isinstance(window_signs, list) else window_signs

                for wf in window_fasts:
                    for ws in window_slows:
                        for wsgn in window_signs:
                            if not all(isinstance(p, (int, float)) for p in [wf, ws, wsgn]):
                                self.log_manager.warning(f"Invalid parameter type for MACD: fast={wf}, slow={ws}, signal={wsgn}. Skipping.")
                                continue
                            macd_indicator = MACD(close=close, window_fast=int(wf), window_slow=int(ws), window_sign=int(wsgn))
                            results_df[f'MACD_macd_{wf}_{ws}_{wsgn}'] = macd_indicator.macd()
                            results_df[f'MACD_signal_{wf}_{ws}_{wsgn}'] = macd_indicator.macd_signal()
                            results_df[f'MACD_diff_{wf}_{ws}_{wsgn}'] = macd_indicator.macd_diff()

            elif indicator_type == 'BollingerBands':
                windows = params.get('window', [20])
                window_devs = params.get('window_dev', [2])

                windows = [windows] if not isinstance(windows, list) else windows
                window_devs = [window_devs] if not isinstance(window_devs, list) else window_devs

                for w in windows:
                    for wd in window_devs:
                        if not all(isinstance(p, (int, float)) for p in [w, wd]):
                            self.log_manager.warning(f"Invalid parameter type for BollingerBands: window={w}, dev={wd}. Skipping.")
                            continue
                        bb = BollingerBands(close=close, window=int(w), window_dev=float(wd))
                        results_df[f'BB_mavg_{w}_{wd}'] = bb.bollinger_mavg()
                        results_df[f'BB_hband_{w}_{wd}'] = bb.bollinger_hband()
                        results_df[f'BB_lband_{w}_{wd}'] = bb.bollinger_lband()
                        results_df[f'BB_wband_{w}_{wd}'] = bb.bollinger_wband()
                        results_df[f'BB_pband_{w}_{wd}'] = bb.bollinger_pband()

            elif indicator_type == 'OBV':
                results_df['OBV'] = OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()

            elif indicator_type == 'VWAP':
                if open_price is None:
                    self.log_manager.error("VWAP calculation requires 'open' column, but it's missing.")
                    return None
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for VWAP: {window}. Skipping.")
                        continue
                    results_df[f'VWAP_{window}'] = VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume, window=int(window)).volume_weighted_average_price()

            elif indicator_type == 'ADX':
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for ADX: {window}. Skipping.")
                        continue
                    adx_indicator = ADXIndicator(high=high, low=low, close=close, window=int(window))
                    results_df[f'ADX_{window}'] = adx_indicator.adx()
                    results_df[f'ADX_pos_{window}'] = adx_indicator.adx_pos()
                    results_df[f'ADX_neg_{window}'] = adx_indicator.adx_neg()

            elif indicator_type == 'AverageTrueRange':
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for AverageTrueRange: {window}. Skipping.")
                        continue
                    results_df[f'ATR_{window}'] = AverageTrueRange(high=high, low=low, close=close, window=int(window)).average_true_range()

            elif indicator_type == 'StochasticOscillator':
                windows = params.get('window', [14])
                smooth_windows = params.get('smooth_window', [3])

                windows = [windows] if not isinstance(windows, list) else windows
                smooth_windows = [smooth_windows] if not isinstance(smooth_windows, list) else smooth_windows

                for w in windows:
                    for sw in smooth_windows:
                        if not all(isinstance(p, (int, float)) for p in [w, sw]):
                            self.log_manager.warning(f"Invalid parameter type for StochasticOscillator: window={w}, smooth_window={sw}. Skipping.")
                            continue
                        stoch_indicator = StochasticOscillator(close=close, high=high, low=low, window=int(w), smooth_window=int(sw))
                        results_df[f'Stoch_k_{w}_{sw}'] = stoch_indicator.stoch()
                        results_df[f'Stoch_d_{w}_{sw}'] = stoch_indicator.stoch_signal()

            elif indicator_type == 'CCI':
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for CCI: {window}. Skipping.")
                        continue
                    results_df[f'CCI_{window}'] = CCIIndicator(high=high, low=low, close=close, window=int(window)).cci()

            elif indicator_type == 'MFI':
                windows = params.get('window', [14])
                windows = [windows] if not isinstance(windows, list) else windows
                for window in windows:
                    if not isinstance(window, (int, float)):
                        self.log_manager.warning(f"Invalid window type for MFI: {window}. Skipping.")
                        continue
                    results_df[f'MFI_{window}'] = MFIIndicator(high=high, low=low, close=close, volume=volume, window=int(window)).money_flow_index()

            elif indicator_type == 'AccDistIndex':
                # AccDistIndex does not take window parameters in ta library
                results_df['ADL'] = acc_dist_index(high=high, low=low, close=close, volume=volume)

            else:
                self.log_manager.warning(f"Unknown indicator type: {indicator_type}")
                return None
            
            if results_df.empty:
                self.log_manager.warning(f"No results generated for indicator type: {indicator_type} with parameters: {params}. Returning None.")
                return None
            
            # If only one column, return as Series, otherwise DataFrame
            if results_df.shape[1] == 1:
                return results_df.iloc[:, 0] # Return the single Series
            return results_df # Return DataFrame for multiple columns

        except Exception as e:
            self.log_manager.error(f"Error calculating {indicator_type}: {str(e)}", exc_info=True)
            return None

    def calculate_indicators_for_dataframe(self, data: pd.DataFrame, indicator_specs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Calculates specified technical indicators (potentially multiple instances of the same indicator
        with different parameters) and appends them to the input DataFrame.

        Args:
            data (pd.DataFrame): The market data DataFrame to which indicators will be added.
                                 Must contain 'close', 'high', 'low', 'volume' columns.
            indicator_specs (List[Dict[str, Any]]): A list where each dictionary represents an
                                                    indicator instance to calculate, including its name
                                                    and specific parameters (e.g., [{"name": "SMA", "window": 10}]).
                                                    Parameters can now be single values or lists of values.

        Returns:
            pd.DataFrame: A new DataFrame with the original data and the calculated indicators appended.
                          Returns an empty DataFrame if the input data is empty or calculation fails.
        """
        if data.empty:
            self.log_manager.warning("Input DataFrame is empty, cannot calculate indicators.")
            return pd.DataFrame()

        df_with_indicators = data.copy()
        calculated_indicators_dict = {}
        
        # Use a counter to ensure unique column names for multiple instances of the same indicator
        # This counter is now less critical as _calculate_single_indicator generates unique names
        # when dealing with list parameters. However, it's still useful for general tracking.
        indicator_instance_counter = defaultdict(int)

        for spec_idx, indicator_spec in enumerate(indicator_specs):
            indicator_name_base = indicator_spec.get("name")
            params = {k: v for k, v in indicator_spec.items() if k != "name"} # Extract actual parameters

            if not indicator_name_base:
                self.log_manager.warning(f"Indicator specification at index {spec_idx} is missing 'name'. Skipping.")
                continue

            # Generate a base unique name. _calculate_single_indicator will append parameter values
            # if parameters are lists.
            param_str_parts = []
            for k, v in sorted(params.items()):
                if isinstance(v, list):
                    param_str_parts.append(f"{k}_[{','.join(map(str, v))}]") # Represent list in name
                else:
                    param_str_parts.append(f"{k}_{v}")
            
            if param_str_parts:
                unique_indicator_name_prefix = f"{indicator_name_base}_{'_'.join(param_str_parts)}"
            else:
                unique_indicator_name_prefix = f"{indicator_name_base}_instance_{indicator_instance_counter[indicator_name_base]}"
            
            indicator_instance_counter[indicator_name_base] += 1

            self.log_manager.info(f"Calculating indicator instance: {unique_indicator_name_prefix} with parameters: {params}")
            calculated_output = self._calculate_single_indicator(data, indicator_name_base, params)
            
            if calculated_output is not None:
                if isinstance(calculated_output, pd.Series):
                    # If _calculate_single_indicator returns a Series, it means it was a single calculation
                    # or it internally handled the list and returned a single series.
                    # We still want a unique name.
                    final_col_name = unique_indicator_name_prefix
                    calculated_indicators_dict[final_col_name] = calculated_output
                elif isinstance(calculated_output, pd.DataFrame):
                    for col in calculated_output.columns:
                        # For DataFrame outputs (e.g., MACD, BollingerBands, or multiple SMA/EMA/RSI)
                        # _calculate_single_indicator already generates unique column names like 'SMA_10', 'SMA_20'
                        # We just need to add them.
                        calculated_indicators_dict[col] = calculated_output[col]
                else:
                    self.log_manager.warning(f"Unexpected return type for {indicator_name_base} instance {unique_indicator_name_prefix}: {type(calculated_output)}. Skipping.")
            else:
                self.log_manager.error(f"Failed to calculate {indicator_name_base} instance {unique_indicator_name_prefix}. Skipping.")

        if calculated_indicators_dict:
            indicators_df = pd.DataFrame(calculated_indicators_dict, index=data.index)
            # Ensure no duplicate columns if original data already has some indicator-like columns
            new_cols = indicators_df.columns.difference(df_with_indicators.columns)
            df_with_indicators = pd.concat([df_with_indicators, indicators_df[new_cols]], axis=1)
        else:
            self.log_manager.warning("No indicators were successfully calculated for the given specs.")

        return df_with_indicators





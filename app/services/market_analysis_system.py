import datetime
import pandas as pd
import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    RandomForestRegressor,
    VotingClassifier
)
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier # Added DecisionTreeClassifier import
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.cluster import KMeans
from sklearn.model_selection import (
    RandomizedSearchCV,
    TimeSeriesSplit,
    cross_val_score
)
from sklearn.preprocessing import (
    StandardScaler,
    LabelEncoder,
    FunctionTransformer
)
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    balanced_accuracy_score,
    f1_score,
    confusion_matrix,
    mean_squared_error, # Added for regression metrics
    r2_score # Added for regression metrics
)
from scipy.stats import randint, uniform, norm, zscore
from scipy.spatial.distance import mahalanobis
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore', category=UserWarning)
# File: app/services/market_analysis_system.py
import warnings
warnings.filterwarnings(
    "ignore",
    message="X has feature names",
    category=UserWarning,
    module="sklearn.utils.validation"
)


from app.services.log_manager import LogManager # Import LogManager

class MarketStateClassifier:
    """
    Class to define and classify market states dynamically.
    """

    def __init__(self, daily_returns: pd.Series, atr_normalized: pd.Series = None):
        """
        Initialize with daily returns and optionally normalized ATR to calculate thresholds dynamically.
        """
        self.daily_returns = daily_returns.dropna()
        self.atr_normalized = atr_normalized.dropna() if atr_normalized is not None else None
        self.market_state_thresholds = self._calculate_market_state_thresholds()
        self.volatility_thresholds = self._calculate_volatility_thresholds() if self.atr_normalized is not None else None

    def _calculate_market_state_thresholds(self) -> dict:
        """
        Calculate market state thresholds dynamically based on standard deviation of daily returns.
        Returns a dictionary with threshold values for market states.
        """
        mean = self.daily_returns.mean()
        std = self.daily_returns.std()

        # Define thresholds relative to mean and std deviation
        thresholds = {
            "extreme_bullish": mean + 2 * std,
            "bullish": mean + std,
            "neutral": mean,
            "bearish": mean - std,
            "extreme_bearish": mean - 2 * std,
        }
        return thresholds

    def _calculate_volatility_thresholds(self) -> dict:
        """
        Calculate volatility thresholds dynamically based on standard deviation of normalized ATR.
        Returns a dictionary with threshold values for volatility regimes.
        """
        mean = self.atr_normalized.mean()
        std = self.atr_normalized.std()

        thresholds = {
            "high": mean + std,
            "medium": mean,
            "low": mean - std,
        }
        return thresholds

    def classify_market_state(self, daily_return: float) -> str:
        """
        Classify a single daily return value into a market state.
        """
        t = self.market_state_thresholds
        if daily_return > t["extreme_bullish"]:
            return "EXTREME_BULLISH"
        elif daily_return > t["bullish"]:
            return "BULLISH"
        elif daily_return >= t["bearish"]:
            return "NEUTRAL"
        elif daily_return >= t["extreme_bearish"]:
            return "BEARISH"
        else:
            return "EXTREME_BEARISH"

    def classify_volatility_regime(self, atr_value: float) -> str:
        """
        Classify a single normalized ATR value into a volatility regime.
        """
        if self.volatility_thresholds is None:
            return "UNKNOWN_VOLATILITY"
        t = self.volatility_thresholds
        if atr_value > t["high"]:
            return "HIGH_VOLATILITY"
        elif atr_value > t["medium"]:
            return "MEDIUM_VOLATILITY"
        elif atr_value > t["low"]:
            return "LOW_VOLATILITY"
        else:
            return "VERY_LOW_VOLATILITY"


class MarketAnalysisSystem:
    """
    A comprehensive system for market data analysis, feature engineering,
    machine learning model training, and prediction.
    """

    def __init__(self, ticker: str, basic_config: Dict[str, Any], advanced_config: Dict[str, Any], log_manager: LogManager):
        """
        Initializes the MarketAnalysisSystem with configurations and a log manager.

        Args:
            ticker (str): The stock ticker symbol.
            basic_config (Dict[str, Any]): Basic configuration settings.
            advanced_config (Dict[str, Any]): Advanced configuration settings.
            log_manager (LogManager): An instance of LogManager for logging.
        """
        self.ticker = ticker
        self.basic_config = basic_config
        self.advanced_config = advanced_config
        self.log_manager = log_manager
        self.market_state_encoder = LabelEncoder()
        self.market_state_mapping = {} # To store the mapping from encoded to original state names

        self.log_manager.info(f"MarketAnalysisSystem initialized for {self.ticker}")

    def _calculate_daily_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the daily return of the 'close' price.
        """
        df['daily_return'] = df['close'].pct_change() * 100
        self.log_manager.info("Daily return calculated.")
        return df



    def _classify_market_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifies the market state (e.g., 'BULLISH', 'BEARISH', 'NEUTRAL')
        based on daily returns and volatility regime, using any 'atr*' column
        produced by the IndicatorCalculator.
        """
        # 1) Ensure 'daily_return' is present
        if 'daily_return' not in df.columns:
            df = self._calculate_daily_return(df)

        # 2) Use MarketStateClassifier to classify market state dynamically
        classifier = MarketStateClassifier(df['daily_return'])
        df['market_state'] = df['daily_return'].apply(classifier.classify_market_state)

        # 3) Classify volatility regime by any ATR column
        #    Find columns that start with 'atr' (e.g. 'atr_14')
        atr_cols = [col for col in df.columns if col.lower().startswith('atr')]
        if atr_cols:
            atr_col = atr_cols[0]
            df['atr_normalized'] = df[atr_col] / df['close']
            atr_normalized = df['atr_normalized']
        else:
            atr_normalized = None

        classifier = MarketStateClassifier(df['daily_return'], atr_normalized)
        if atr_normalized is not None:
            df['volatility_regime'] = df['atr_normalized'].apply(classifier.classify_volatility_regime)
        else:
            df['volatility_regime'] = 'UNKNOWN_VOLATILITY'
            self.log_manager.warning(
                "No ATR* column found for volatility regime classification. Skipping."
            )

        self.log_manager.info("Market state and volatility regime classified.")
        return df


    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs feature engineering on the market data.
        This method is modified to respect the new configuration flags
        and exclude certain features as per user request.
        """
        self.log_manager.info("Starting feature engineering.")

        # Ensure daily_return is calculated
        if 'daily_return' not in df.columns:
            df = self._calculate_daily_return(df)

        # === Lagged Features (Adjusted based on user request) ===
        # Exclude direct open, high, low, close lags
        lag_features = ['daily_return', 'volume'] # Only daily_return and volume lags are considered
        lags = [1, 3, 5] # Example lags

        for feature in lag_features:
            if feature == 'volume' and not self.basic_config.get('use_volume_features', True):
                continue # Skip volume lags if use_volume_features is False

            for lag in lags:
                df[f'{feature}_lag_{lag}'] = df[feature].shift(lag)

        # === Rolling Window Features (Adjusted based on user request) ===
        # Exclude open_rolling_mean, high_rolling_mean, low_rolling_mean, close_rolling_mean
        # Only daily_return rolling means are considered here.
        # Rolling standard deviation for 'close' is conditional.
        rolling_windows = [5, 10]

        for window in rolling_windows:
            df[f'daily_return_rolling_mean_{window}'] = df['daily_return'].rolling(window=window).mean()
            df[f'daily_return_rolling_std_{window}'] = df['daily_return'].rolling(window=window).std()
            
            # Conditional: close_rolling_std based on config
            if self.basic_config.get('use_price_std_features', True):
                df[f'close_rolling_std_{window}'] = df['close'].rolling(window=window).std()


        # === Interaction Features (Adjusted based on user request) ===
        if self.basic_config.get('use_volume_features', True):
            # Example: Interaction between close price and volume
            df['close_volume_interaction'] = df['close'] * df['volume']

        # Drop rows with NaN values created by feature engineering
        initial_rows = len(df)
        df.dropna(inplace=True)
        dropped_rows = initial_rows - len(df)
        if dropped_rows > 0:
            self.log_manager.info(f"Dropped {dropped_rows} rows due to NaN values after feature engineering.")
        
        self.log_manager.info("Feature engineering complete.")
        return df

    def _prepare_data_for_ml(self, df: pd.DataFrame, target_horizon: int, prediction_type: str) -> Tuple[pd.DataFrame, pd.Series, LabelEncoder]:
        """
        Prepares the DataFrame for machine learning, including target variable creation,
        feature selection (if configured), and scaling.
        """
        self.log_manager.info("Preparing data for machine learning.")

        # Create target variable based on prediction_type
        if prediction_type == 'classification':
            # Shift market_state to create the target variable for the future horizon
            df['target_market_state'] = df['market_state'].shift(-target_horizon)
            # Drop the last 'target_horizon' rows as their target is NaN
            df.dropna(subset=['target_market_state'], inplace=True)
            
            # Encode target market state
            # Fit and transform only on the available target states
            self.market_state_encoder.fit(df['market_state'].unique())
            df['target_market_state_encoded'] = self.market_state_encoder.transform(df['target_market_state'])
            
            # Store the mapping for decoding later
            self.market_state_mapping = dict(zip(self.market_state_encoder.transform(self.market_state_encoder.classes_), self.market_state_encoder.classes_))
            self.log_manager.info(f"Market State encoded: {self.market_state_mapping}")
            
            target = df['target_market_state_encoded']
            # Drop original market_state and target_market_state from features
            features_df = df.drop(columns=['market_state', 'target_market_state', 'target_market_state_encoded'], errors='ignore')
        
        elif prediction_type == 'regression':
            # Use 'close' price as target for regression, shifted to the future
            df['target_price'] = df['close'].shift(-target_horizon)
            df.dropna(subset=['target_price'], inplace=True)
            target = df['target_price']
            features_df = df.drop(columns=['target_price'], errors='ignore') # Drop target from features
            # Also drop market_state and volatility_regime if they were created for classification
            features_df = features_df.drop(columns=['market_state', 'volatility_regime'], errors='ignore')
        else:
            raise ValueError(f"Unsupported prediction_type: {prediction_type}")

        # Drop non-numeric columns that are not features (e.g., 'volatility_regime' if not encoded)
        # Ensure 'market_state' and 'volatility_regime' are dropped if they are not encoded
        features_df = features_df.select_dtypes(include=np.number)
        
        # Drop any columns that are all NaN after feature engineering and target creation
        features_df.dropna(axis=1, how='all', inplace=True)
        
        # Drop original OHLCV columns if they are not intended as direct features
        # Based on user request, direct OHLCV and their lags are excluded.
        # However, 'close' and 'volume' are needed for daily_return, rolling_std, and interaction features.
        # We need to ensure they are not passed as direct features to the model.
        # The feature engineering step already handles which lags are created.
        # Here, we ensure the base OHLCV columns are not part of the final feature set.
        columns_to_drop_after_feature_creation = ['open', 'high', 'low', 'close', 'volume']
        features_df = features_df.drop(columns=[col for col in columns_to_drop_after_feature_creation if col in features_df.columns], errors='ignore')

        # Drop any remaining NaN values that might have been introduced
        # This is a final safeguard, as feature engineering already has a dropna
        initial_features_rows = len(features_df)
        combined_df = pd.concat([features_df, target], axis=1).dropna()
        features_df = combined_df.drop(columns=[target.name])
        target = combined_df[target.name]
        
        if len(features_df) < initial_features_rows:
            self.log_manager.info(f"Dropped {initial_features_rows - len(features_df)} rows during final data preparation due to NaNs.")


        # Scale features
        scaler = StandardScaler()
        # Fit scaler only on training data in cross-validation, but for simplicity here, fit on all data
        # In a production system, this would be part of the pipeline inside cross-validation.
        scaled_features = scaler.fit_transform(features_df)
        features_df_scaled = pd.DataFrame(scaled_features, index=features_df.index, columns=features_df.columns)

        self.log_manager.info("Data preparation for machine learning complete.")
        return features_df_scaled, target, scaler

    def _get_model_pipeline(self, model_name: str, prediction_type: str):
        """
        Returns a scikit-learn pipeline for the specified model, including a scaler.
        Ensures models are correctly initialized before usage.
        """
        model = None

        if prediction_type == 'classification':
            classifiers = {
                'RandomForestClassifier': RandomForestClassifier(n_estimators=100, random_state=42),
                'LogisticRegression': LogisticRegression(random_state=42, solver='liblinear'),
                'XGBClassifier': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
                'LGBMClassifier': LGBMClassifier(random_state=42),
                'SVC': SVC(random_state=42, probability=True),
                'GradientBoostingClassifier': GradientBoostingClassifier(random_state=42),
                'AdaBoostClassifier': AdaBoostClassifier(random_state=42),
                'GaussianNB': GaussianNB(),
                'KNeighborsClassifier': KNeighborsClassifier(),
                'LinearDiscriminantAnalysis': LinearDiscriminantAnalysis(),
                'QuadraticDiscriminantAnalysis': QuadraticDiscriminantAnalysis(),
                'DecisionTreeClassifier': DecisionTreeClassifier(random_state=42),
                'CatBoostClassifier': CatBoostClassifier(random_state=42, verbose=0)
            }
            model = classifiers.get(model_name, None)
        
        elif prediction_type == 'regression':
            regressors = {
                'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42),
                # Add other regression models here if needed
            }
            model = regressors.get(model_name, None)

        if model:
            pipeline = Pipeline(steps=[('scaler', StandardScaler()), ('model', model)])
            
            # 🚀 بررسی `estimators_` قبل از اجرا
            if model_name == 'RandomForestClassifier':
                try:
                    if not hasattr(model, "estimators_"):
                        raise ValueError(f"{model_name} has not been trained. Call `fit()` before accessing `estimators_`.")
                except Exception as e:
                    print(f"Error in model initialization: {e}")

            return pipeline
        
        return None

    def _evaluate_model(self, model_pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, prediction_type: str) -> Dict[str, Any]:
        """
        Evaluates the model using time series cross-validation and returns performance metrics.
        Includes hyperparameter tuning with RandomizedSearchCV.
        """
        n_splits = self.advanced_config.get("n_splits", 5)
        test_size_ratio = self.advanced_config.get("test_size", 0.2)
        random_state = self.advanced_config.get("random_state", 42)

        tscv = TimeSeriesSplit(n_splits=n_splits)

        param_distributions = {}
        model_name = model_pipeline.named_steps['model'].__class__.__name__

        # Define hyperparameter distributions for tuning
        if model_name == 'RandomForestClassifier' or model_name == 'RandomForestRegressor':
            param_distributions = {
                'model__n_estimators': randint(50, 100),
                'model__max_depth': randint(3, 20),
                'model__min_samples_leaf': randint(1, 5),
                'model__min_samples_split': randint(2, 10),
            }
        elif model_name == 'XGBClassifier':
            param_distributions = {
                'model__n_estimators': randint(50, 100),
                'model__max_depth': randint(3, 10),
                'model__learning_rate': uniform(0.01, 0.3),
            }
        # Add more models' hyperparameters here

        if param_distributions:
            self.log_manager.info(f"Training and evaluating {model_name} for {prediction_type} task.")
            search = RandomizedSearchCV(
                model_pipeline,
                param_distributions,
                n_iter=10, # Number of parameter settings that are sampled
                cv=tscv,
                scoring='balanced_accuracy' if prediction_type == 'classification' else 'neg_mean_squared_error',
                random_state=random_state,
                n_jobs=-1, # Use all available cores
                verbose=0 # Suppress verbose output from RandomizedSearchCV
            )
            search.fit(X, y)
            best_model = search.best_estimator_
            best_params = search.best_params_
            self.log_manager.info(f"Best parameters for {model_name}: {best_params}")
        else:
            self.log_manager.info(f"Training and evaluating {model_name} for {prediction_type} task (no hyperparameter tuning).")
            best_model = model_pipeline
            best_model.fit(X, y)
            best_params = {}

        y_pred = best_model.predict(X)
        metrics = {}

        if prediction_type == 'classification':
            metrics['balanced_accuracy'] = balanced_accuracy_score(y, y_pred)
            metrics['f1_weighted'] = f1_score(y, y_pred, average='weighted')
            metrics['classification_report'] = classification_report(y, y_pred, output_dict=True)
            metrics['confusion_matrix'] = confusion_matrix(y, y_pred).tolist() # Convert to list for JSON serialization

            # Cross-validation scores
            cv_scores = cross_val_score(best_model, X, y, cv=tscv, scoring='balanced_accuracy', n_jobs=-1)
            metrics['cross_val_accuracy_mean'] = np.mean(cv_scores)
            metrics['cross_val_accuracy_std'] = np.std(cv_scores)

        elif prediction_type == 'regression':
            metrics['mean_squared_error'] = mean_squared_error(y, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mean_squared_error'])
            metrics['r2_score'] = r2_score(y, y_pred)

            # Cross-validation scores
            cv_scores = cross_val_score(best_model, X, y, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
            metrics['cross_val_rmse_mean'] = np.mean(np.sqrt(-cv_scores))
            metrics['cross_val_rmse_std'] = np.std(np.sqrt(-cv_scores))

        metrics['best_params'] = best_params
        # Remove the best_model from metrics before returning to avoid JSON serialization issues
        if 'best_model' in metrics:
            del metrics['best_model']

        self.log_manager.info(f"Evaluation for {model_name} complete. Metrics: {metrics}")
        return metrics

    def _forecast_future_market_state(self, model: Pipeline, X_latest: pd.DataFrame) -> str:
        """
        Forecasts the future market state using the trained classification model.
        """
        self.log_manager.info("Forecasting future market states.")
        if not X_latest.empty:
            # Predict the encoded state
            predicted_encoded_state = model.predict(X_latest)[0]
            # Decode the predicted state
            predicted_state = self.market_state_mapping.get(predicted_encoded_state, "UNKNOWN")
            self.log_manager.info("Market state forecasting complete.")
            return predicted_state
        self.log_manager.warning("No latest data available for market state forecasting.")
        return "N/A"

    def _forecast_future_price_range(self, model: Pipeline, X_latest: pd.DataFrame) -> Tuple[float, float]:
        """
        Forecasts the future price range using the trained regression model.
        For simplicity, we'll use a simple prediction and a confidence interval (e.g., based on std dev of residuals).
        """
        self.log_manager.info("Forecasting future price ranges.")
        if not X_latest.empty:
            predicted_price = model.predict(X_latest)[0]
            # A very basic way to estimate range: +/- 2 standard deviations of residuals from training
            # This is a simplification; a proper prediction interval would be more complex.
            # For demonstration, we'll just use a fixed percentage or a placeholder.
            
            # If we had access to training residuals, we could calculate their std dev.
            # For now, let's assume a fixed percentage for range estimation.
            # This needs to be refined if actual prediction intervals are required.
            range_percentage = 0.02 # 2% of predicted price
            lower_bound = predicted_price * (1 - range_percentage)
            upper_bound = predicted_price * (1 + range_percentage)

            self.log_manager.info("Price range forecasting complete.")
            return float(lower_bound), float(upper_bound)
        self.log_manager.warning("No latest data available for price range forecasting.")
        return np.nan, np.nan


    def _calculate_feature_importances(self, model_pipeline: Pipeline, X: pd.DataFrame, method: str = "permutation_importance") -> Dict[str, float]:
        """
        Calculates and returns feature importances.
        """
        self.log_manager.info("Calculating feature importances.")
        importances = {}
        model = model_pipeline.named_steps['model']

        if hasattr(model, 'feature_importances_') and method == "tree_based":
            # For tree-based models like RandomForest, XGBoost, LightGBM
            importances_array = model.feature_importances_
            importances = dict(zip(X.columns, importances_array))
        elif method == "permutation_importance":
            try:
                from sklearn.inspection import permutation_importance
                result = permutation_importance(model, X, model.predict(X), n_repeats=10, random_state=42, n_jobs=-1)
                sorted_idx = result.importances_mean.argsort()
                importances = dict(zip(X.columns[sorted_idx], result.importances_mean[sorted_idx]))
            except ImportError:
                self.log_manager.warning("sklearn.inspection.permutation_importance not found. Skipping permutation importance.")
                importances = {}
            except Exception as e:
                self.log_manager.error(f"Error calculating permutation importance: {e}", exc_info=True)
                importances = {}
        # Add SHAP or other methods here if needed

        # Convert to percentage and sort
        total_importance = sum(importances.values())
        if total_importance > 0:
            importances_percent = {k: (v / total_importance) * 100 for k, v in importances.items()}
            sorted_importances = dict(sorted(importances_percent.items(), key=lambda item: item[1], reverse=True))
        else:
            sorted_importances = {}
            self.log_manager.warning("Total feature importance is zero. Cannot normalize to percentage.")

        self.log_manager.info("Feature importances calculated successfully.")
        return sorted_importances

    def _determine_current_market_state(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Determines the current market state and volatility regime based on the latest data.
        """
        self.log_manager.info("Current market state determined.")
        if df.empty:
            self.log_manager.warning("DataFrame is empty, cannot determine current market state.")
            return {"current_market_state": "N/A", "current_volatility_regime": "N/A"}

        latest_data = df.iloc[-1]
        current_state = latest_data.get('market_state', 'N/A')
        current_volatility = latest_data.get('volatility_regime', 'N/A')

        return {
            "current_market_state": current_state,
            "current_volatility_regime": current_volatility,
            "latest_daily_return": float(latest_data.get('daily_return', np.nan))
        }


    def run_analysis_pipeline(self, df: pd.DataFrame, prediction_horizons: List[int]) -> Dict[str, Any]:
        """
        Runs the full market analysis pipeline.

        Args:
            df (pd.DataFrame): The input market data (OHLCV).
            prediction_horizons (List[int]): List of prediction horizons (e.g., [1, 5, 10] days).

        Returns:
            Dict[str, Any]: A dictionary containing all collected analysis data.
        """
        analysis_data = {
            "ticker": self.ticker,
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "basic_config": self.basic_config,
            "advanced_config": self.advanced_config,
            "data_summary": {},
            "market_state_info": {},
            "model_performance": {},
            "feature_importances": {},
            "forecasts": {},
            "indicator_info": {} # This will be populated by ReportDataCollector if optimization is done
        }

        # Check for empty dataframe or missing 'close' column early
        if df.empty:
            self.log_manager.error("Input DataFrame is empty. Exiting pipeline.")
            return {}
        if 'close' not in df.columns:
            self.log_manager.error("Input DataFrame missing required 'close' column. Exiting pipeline.")
            return {}

        # Ensure column names are lowercase for consistency
        df.columns = df.columns.str.lower()
        self.log_manager.info("DataFrame columns converted to lowercase.")

        # Step 1: Calculate Daily Return
        df = self._calculate_daily_return(df)

        # Step 2: Classify Market State and Volatility Regime
        df = self._classify_market_state(df)
        analysis_data["market_state_info"]["historical_states"] = df['market_state'].value_counts().to_dict()
        analysis_data["market_state_info"]["historical_volatility_regimes"] = df['volatility_regime'].value_counts().to_dict()

        # Step 3: Feature Engineering (Conditional based on config)
        if self.basic_config.get('enable_feature_engineering', True):
            df = self._feature_engineering(df)
        else:
            self.log_manager.info("Feature engineering is disabled by configuration.")
            # If feature engineering is disabled, we might still need to drop NaNs from initial calculations
            initial_rows = len(df)
            df.dropna(inplace=True)
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                self.log_manager.info(f"Dropped {dropped_rows} rows due to NaN values after initial calculations (feature engineering disabled).")


        # Store data summary before ML preparation
        analysis_data["data_summary"] = {
            "total_candles": len(df),
            "start_date": df.index.min().strftime("%Y-%m-%d") if not df.empty else "N/A",
            "end_date": df.index.max().strftime("%Y-%m-%d") if not df.empty else "N/A",
            "columns": df.columns.tolist()
        }
        if df.empty:
            self.log_manager.error("DataFrame is empty after feature engineering/initial processing. Cannot proceed with ML.")
            return {}

        # Step 4: Prepare Data for Machine Learning for each horizon
        for horizon in prediction_horizons:
            horizon_config = self.advanced_config["prediction_horizons_config"].get(horizon, {})
            selected_models_for_horizon = horizon_config.get("models", self.basic_config["selected_models"])
            prediction_type = self.basic_config["prediction_type"] # Use global prediction type for now

            X, y, scaler = self._prepare_data_for_ml(df.copy(), horizon, prediction_type) # Pass a copy of df

            if X.empty or y.empty:
                self.log_manager.warning(f"Skipping ML for horizon {horizon} due to empty data after preparation.")
                continue

            analysis_data["model_performance"][horizon] = {}
            analysis_data["feature_importances"][horizon] = {}
            analysis_data["forecasts"][horizon] = {}

            # Get the latest features for forecasting
            X_latest = X.iloc[[-1]] # Take the last row for forecasting

            for model_name in selected_models_for_horizon:
                model_pipeline = self._get_model_pipeline(model_name, prediction_type)
                if model_pipeline:
                    self.log_manager.info(f"Processing model {model_name} for horizon {horizon}.")
                    metrics = self._evaluate_model(model_pipeline, X, y, prediction_type)
                    analysis_data["model_performance"][horizon][model_name] = metrics

                    # Calculate feature importances based on the best model from tuning
                    if metrics and 'best_model' in metrics:
                        feature_importances = self._calculate_feature_importances(
                            metrics['best_model'], X, self.advanced_config.get("feature_selection_method", "permutation_importance")
                        )
                        analysis_data["feature_importances"][horizon][model_name] = feature_importances

                        # Forecast future state/price using the best model and latest data
                        if prediction_type == 'classification':
                            forecasted_state = self._forecast_future_market_state(metrics['best_model'], X_latest)
                            analysis_data["forecasts"][horizon][model_name] = {"predicted_market_state": forecasted_state}
                        elif prediction_type == 'regression':
                            lower_bound, upper_bound = self._forecast_future_price_range(metrics['best_model'], X_latest)
                            analysis_data["forecasts"][horizon][model_name] = {"predicted_price_range": (lower_bound, upper_bound)}
                else:
                    self.log_manager.warning(f"Skipping unsupported model: {model_name} for {prediction_type} task.")

        # Determine current market state based on the latest available data after all processing
        analysis_data["market_state_info"]["current_state_details"] = self._determine_current_market_state(df)

        self.log_manager.info("Full market analysis pipeline complete.")
        return analysis_data

    def _get_model_pipeline(self, model_name: str, prediction_type: str):
        """
        Returns a scikit-learn pipeline for the specified model, including a scaler.
        Uses `is not None` to avoid accidental __len__() calls on unfitted estimators.
        """
        model = None

        if prediction_type == 'classification':
            if model_name == 'RandomForestClassifier':
                model = RandomForestClassifier(random_state=42)
            elif model_name == 'LogisticRegression':
                model = LogisticRegression(random_state=42, solver='liblinear')
            elif model_name == 'XGBClassifier':
                model = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss')
            elif model_name == 'LGBMClassifier':
                model = LGBMClassifier(random_state=42)
            elif model_name == 'SVC':
                model = SVC(random_state=42, probability=True)
            elif model_name == 'GradientBoostingClassifier':
                model = GradientBoostingClassifier(random_state=42)
            elif model_name == 'AdaBoostClassifier':
                model = AdaBoostClassifier(random_state=42)
            elif model_name == 'GaussianNB':
                model = GaussianNB()
            elif model_name == 'KNeighborsClassifier':
                model = KNeighborsClassifier()
            elif model_name == 'LinearDiscriminantAnalysis':
                model = LinearDiscriminantAnalysis()
            elif model_name == 'QuadraticDiscriminantAnalysis':
                model = QuadraticDiscriminantAnalysis()
            elif model_name == 'DecisionTreeClassifier':
                model = DecisionTreeClassifier(random_state=42)
            elif model_name == 'CatBoostClassifier':
                model = CatBoostClassifier(random_state=42, verbose=0)

        elif prediction_type == 'regression':
            if model_name == 'RandomForestRegressor':
                model = RandomForestRegressor(random_state=42)
            # Add other regression models here if needed

        # این‌جا به‌جای "if model:" صراحتاً None را چک می‌کنیم
        if model is not None:
            return Pipeline(steps=[('scaler', StandardScaler()), ('model', model)])
        else:
            return None
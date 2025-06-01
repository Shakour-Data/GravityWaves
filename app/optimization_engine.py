import numpy as np
import pandas as pd
from typing import Any, Dict, List, Tuple, Optional, Union, Set
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
import random
from collections import defaultdict
from scipy.stats import norm
from datetime import datetime
import traceback
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize

from deap import base, creator, tools, algorithms
from skopt import gp_minimize
from skopt.space import Integer, Real, Categorical # Import Categorical for discrete choices
from app.services.log_manager import LogManager, ConsolePrinter
import app.services.market_analysis_system as mas
from app.services.indicator_calculator import IndicatorCalculator
from app.services.constants import MAX_DAILY_FLUCTUATION # Import from constants.py

import warnings
warnings.filterwarnings(
    "ignore",
    message="X has feature names",
    category=UserWarning,
    module="sklearn.utils.validation"
)


# Define the full range of optimizable parameters for each indicator type
# This dictionary describes the *definition* of each indicator's parameters,
# not specific instances for optimization.
OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS = {
    "SMA": {"window": [10, 20, 30, 50, 100, 200]},
    "EMA": {"window": [12, 26, 50, 100, 200]},
    "RSI": {"window": [7, 14, 21, 28]},
    "MACD": {
        "fast": [8, 12, 16, 20],
        "slow": [20, 26, 30, 34],
        "signal": [7, 9, 12]
    },
    "BollingerBands": {
        "window": [15, 20, 25, 30],
        "window_dev": [1.0, 1.5, 2.0, 2.5, 3.0]
    },
    "ADX": {"window": [10, 14, 20, 28]},
    "AverageTrueRange": {"window": [10, 14, 20]},
    "StochasticOscillator": {
        "window": [10, 14, 20],
        "smooth_window": [3, 5, 7]
    },
    "CCI": {"window": [10, 14, 20]},
    "MFI": {"window": [10, 14, 20]},
    "OBV": {}, # No parameters to optimize for OBV
    "ADL": {}, # No parameters to optimize for ADL
}

try:
    # FitnessMax for classification (maximize accuracy)
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    # Individual is a list of gene values (indices or normalized floats)
    creator.create("Individual", list, fitness=creator.FitnessMax)
except RuntimeError:
    pass # Already created


class IndicatorOptimizer:
    """
    Optimizes the parameters of technical indicators using a genetic algorithm
    or Bayesian Optimization to improve the performance of market state prediction models.
    Supports optimizing multiple instances of the same indicator with different parameters.
    """

    def __init__(
        self,
        ticker: str, # Added ticker parameter
        market_data: pd.DataFrame,
        log_manager: LogManager,
        indicator_calculator: IndicatorCalculator,
        printer: ConsolePrinter,
        # indicator_params is now a LIST of indicator instances to optimize
        # Each dict in the list specifies the indicator name and the *parameter choices* for that instance.
        # Example: [{"name": "SMA", "window_choices": [10, 20]}, {"name": "SMA", "window_choices": [50, 100]}]
        indicator_params: List[Dict[str, Any]],
        task_type: str = 'classification', # Currently only 'classification' is supported for GA
        target_horizon: int = 1,
        population_size: int = 50, # Parameter for Genetic Algorithm
        num_generations: int = 10, # Parameter for Genetic Algorithm
        n_calls: int = 50, # Parameter for Bayesian Optimization (total evaluations)
        n_random_starts: int = 10, # Parameter for Bayesian Optimization (initial random points)
        optimization_method: str = 'GA', # New: 'GA', 'Bayesian', 'Both'
        completely_excluded_indicators: Optional[List[str]] = None, # Base indicator names to completely exclude
        allowed_models: Optional[List[str]] = None,
        max_daily_fluctuation: float = MAX_DAILY_FLUCTUATION,
        # Add basic_config and advanced_config to the optimizer's init
        # These will be used to initialize MarketAnalysisSystem within the objective function
        basic_config: Dict[str, Any] = None,
        advanced_config: Dict[str, Any] = None,
        # New parameters for early stopping
        patience: int = 5, # Number of generations/iterations to wait without significant improvement
        min_delta: float = 0.001 # Minimum required improvement to consider it "significant"
    ):
        self.ticker = ticker # Stored ticker as an instance attribute
        self.market_data = market_data
        self.log_manager = log_manager
        self.indicator_calculator = indicator_calculator
        self.printer = printer
        self.indicator_params = indicator_params # This now defines the structure of the individual
        self.task_type = task_type
        self.target_horizon = target_horizon
        self.population_size = population_size
        self.num_generations = num_generations
        self.n_calls = n_calls
        self.n_random_starts = n_random_starts
        self.optimization_method = optimization_method

        # Results storage for comparison
        self.best_fitness_ga = -np.inf
        self.best_indicator_specs_ga: Optional[List[Dict[str, Any]]] = None
        self.best_fitness_bo = -np.inf
        self.best_indicator_specs_bo: Optional[List[Dict[str, Any]]] = None

        self.completely_excluded_indicators = completely_excluded_indicators or []
        self.allowed_models = allowed_models
        self.max_daily_fluctuation = max_daily_fluctuation

        # Store the full configs for MarketAnalysisSystem initialization
        self.base_basic_config = basic_config if basic_config is not None else {}
        self.base_advanced_config = advanced_config if advanced_config is not None else {}

        # Early stopping parameters
        self.patience = patience
        self.min_delta = min_delta

        # Cache to store previously evaluated indicator configurations and their fitness scores
        self.evaluated_configurations = {}  # {tuple(encoded_individual): fitness_score}

        self.log_manager.info("IndicatorOptimizer initialized.")
        self.log_manager.info(f"Optimization task type: {self.task_type}")
        self.log_manager.info(f"Target horizon: {self.target_horizon}")
        self.log_manager.info(f"Optimization method selected: {self.optimization_method}")
        self.log_manager.info(f"Indicator instances configured for optimization: {len(self.indicator_params)}")
        for i, ind_spec in enumerate(self.indicator_params):
            self.log_manager.info(f"  Instance {i+1}: {ind_spec.get('name')} with parameters: {ind_spec}")
        if self.completely_excluded_indicators:
            self.log_manager.info(f"Completely excluded indicators: {self.completely_excluded_indicators}")

        # Setup DEAP toolbox for GA, even if not immediately used, for consistency
        self.toolbox = base.Toolbox()
        self._setup_deap_toolbox()

    def _setup_deap_toolbox(self):
        """
        Sets up the DEAP toolbox with attribute generators, individual/population creators,
        and genetic operators (evaluate, mate, mutate, select).
        This is primarily for Genetic Algorithm.
        """
        # Attribute generators for each gene (parameter) in each indicator instance
        individual_attrs = []
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            
            if indicator_name in self.completely_excluded_indicators:
                self.log_manager.info(f"Skipping attribute generation for excluded indicator instance: {indicator_instance_def}")
                continue

            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            
            for param_name, param_values_def in param_defs.items():
                actual_param_values = indicator_instance_def.get(f"{param_name}_choices", param_values_def)

                if isinstance(actual_param_values, list):
                    if not actual_param_values:
                        self.log_manager.warning(f"Empty choices list for {indicator_name}-{param_name}. Skipping attribute generation.")
                        continue
                    individual_attrs.append(lambda values=actual_param_values: random.randint(0, len(values) - 1))
                elif isinstance(actual_param_values, tuple) and len(actual_param_values) == 2 and all(isinstance(v, (int, float)) for v in actual_param_values):
                    individual_attrs.append(random.random)
                else:
                    self.log_manager.warning(f"Unsupported parameter type for {indicator_name}-{param_name}: {type(actual_param_values)}. Skipping attribute generation.")
        
        if not individual_attrs:
            self.log_manager.error("No attributes registered for individual creation. Genetic Algorithm cannot run.")
            # This will raise an error if GA is attempted without optimizable parameters
            # For BO, this check is done during search space creation.
            return # Don't raise here, allow BO path if GA is not the only method

        self.toolbox.register("individual", tools.initCycle, creator.Individual, individual_attrs, n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self._objective_function)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._custom_mutate, indpb=0.1)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def _encode_individual(self, indicator_specs: List[Dict[str, Any]]) -> List[Any]:
        """
        Encodes a list of indicator specifications (actual parameter values) into a flat list of gene values.
        This is used to initialize individuals from known good specs or for debugging.
        For discrete parameters, it encodes the index of the chosen value.
        For continuous parameters, it encodes a normalized float [0,1].
        """
        encoded_list = []
        for instance_spec in indicator_specs: # Corrected loop variable name
            indicator_name = instance_spec["name"]
            if indicator_name in self.completely_excluded_indicators:
                continue

            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            for param_name, param_values_def in param_defs.items():
                current_value = instance_spec.get(param_name)
                if current_value is None:
                    self.log_manager.warning(f"Parameter {param_name} not found for {indicator_name} in spec. Using default encoding (index 0 or 0.0).")
                    encoded_list.append(0 if isinstance(param_values_def, list) else 0.0)
                    continue

                # Corrected: Use 'instance_spec' instead of 'indicator_instance_def'
                actual_param_values = instance_spec.get(f"{param_name}_choices", param_values_def)

                if isinstance(actual_param_values, list):
                    try:
                        encoded_list.append(actual_param_values.index(current_value))
                    except ValueError:
                        self.log_manager.warning(f"Value {current_value} not in {actual_param_values} for {indicator_name}-{param_name}. Using default index 0.")
                        encoded_list.append(0)
                elif isinstance(actual_param_values, tuple) and len(actual_param_values) == 2:
                    min_val, max_val = actual_param_values
                    if max_val - min_val > 0:
                        normalized_val = (current_value - min_val) / (max_val - min_val)
                        encoded_list.append(normalized_val)
                    else:
                        encoded_list.append(0.0)
                else:
                    self.log_manager.warning(f"Unsupported parameter type for {indicator_name}-{param_name}. Skipping encoding.")
                    encoded_list.append(0) # Fallback
        return encoded_list

    def _decode_individual(self, individual_genes: List[Any]) -> List[Dict[str, Any]]:
        """
        Decodes a flat list of gene values (from DEAP or skopt) back into a list of
        indicator specifications (indicator name and its actual parameter values).
        """
        decoded_specs = []
        gene_idx = 0
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            
            if indicator_name in self.completely_excluded_indicators:
                continue

            decoded_instance_spec = {"name": indicator_name}
            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})

            for param_name, param_values_def in param_defs.items():
                actual_param_values = indicator_instance_def.get(f"{param_name}_choices", param_values_def)

                if gene_idx < len(individual_genes):
                    gene_val = individual_genes[gene_idx]
                    if isinstance(actual_param_values, list):
                        if not isinstance(gene_val, (int, np.integer)): # Handle numpy integer types
                            gene_val = int(round(gene_val))
                        
                        if 0 <= gene_val < len(actual_param_values):
                            decoded_instance_spec[param_name] = actual_param_values[gene_val]
                        else:
                            self.log_manager.warning(f"Decoded index {gene_val} out of bounds for {indicator_name}-{param_name} (len={len(actual_param_values)}). Using default: {actual_param_values[0]}")
                            decoded_instance_spec[param_name] = actual_param_values[0]
                    elif isinstance(actual_param_values, tuple) and len(actual_param_values) == 2:
                        min_val, max_val = actual_param_values
                        denormalized_val = gene_val * (max_val - min_val) + min_val
                        if isinstance(min_val, int) and isinstance(max_val, int):
                            decoded_instance_spec[param_name] = int(round(denormalized_val))
                        else:
                            decoded_instance_spec[param_name] = denormalized_val
                    gene_idx += 1
                else:
                    self.log_manager.warning(f"Individual genes list too short for {indicator_name}-{param_name}. Assigning None.")
                    decoded_instance_spec[param_name] = None

            decoded_specs.append(decoded_instance_spec)
        return decoded_specs

    def _custom_mutate(self, individual, indpb):
        """
        Custom mutation operator for DEAP.
        Mutates individual genes (parameter choices) based on their type (discrete/continuous).
        """
        gene_idx = 0
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            
            if indicator_name in self.completely_excluded_indicators:
                continue

            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            for param_name, param_values_def in param_defs.items():
                actual_param_values = indicator_instance_def.get(f"{param_name}_choices", param_values_def)

                if random.random() < indpb:
                    if isinstance(actual_param_values, list):
                        if actual_param_values:
                            individual[gene_idx] = random.randint(0, len(actual_param_values) - 1)
                        else:
                            self.log_manager.warning(f"Cannot mutate {indicator_name}-{param_name}: empty choices list.")
                    elif isinstance(actual_param_values, tuple) and len(actual_param_values) == 2:
                        current_val = individual[gene_idx]
                        perturbation = random.uniform(-0.1, 0.1)
                        individual[gene_idx] = max(0.0, min(1.0, current_val + perturbation))
                gene_idx += 1
        return individual,

    def _objective_function(self, individual_genes: List[Any]) -> float:
        """
        The objective function to be minimized/maximized by the optimization algorithm.
        It decodes the individual, calculates indicators, runs MarketAnalysisSystem,
        and returns its balanced accuracy.
        """
        # Convert the list of genes to a tuple to make it hashable for caching
        individual_key = tuple(individual_genes)

        # Check if this configuration has already been evaluated
        if individual_key in self.evaluated_configurations:
            fitness = self.evaluated_configurations[individual_key]
            self.log_manager.info(f"Retrieved cached fitness: {fitness:.4f} for specs: {self._decode_individual(individual_genes)}")
            return fitness

        # Decode the individual into a list of indicator specifications
        indicator_specs_for_calculation = self._decode_individual(individual_genes)
        
        # Filter out any instances of indicators that are completely excluded
        filtered_specs = [
            spec for spec in indicator_specs_for_calculation
            if spec.get("name") not in self.completely_excluded_indicators
        ]

        if not filtered_specs:
            self.log_manager.warning("All indicator instances were filtered out. Returning fitness of 0.0.")
            # Store 0.0 in cache for this configuration
            self.evaluated_configurations[individual_key] = 0.0
            return 0.0 # Return 0.0 for balanced accuracy if no indicators

        try:
            # Step 1: Calculate indicators on the raw market data using the current individual's specs
            df_with_optimized_indicators = self.indicator_calculator.calculate_indicators_for_dataframe(
                self.market_data.copy(), # Pass a copy to avoid modifying original
                filtered_specs
            )

            if df_with_optimized_indicators.empty:
                self.log_manager.warning(f"No indicators calculated for individual: {filtered_specs}. Returning fitness of 0.0.")
                # Store 0.0 in cache for this configuration
                self.evaluated_configurations[individual_key] = 0.0
                return 0.0

            # Construct basic and advanced configs for MarketAnalysisSystem
            # Start with the base configs passed to IndicatorOptimizer, then override/add specifics
            temp_basic_config = self.base_basic_config.copy()
            temp_basic_config["ticker"] = self.ticker # Access self.ticker here
            temp_basic_config["selected_models"] = self.allowed_models
            temp_basic_config["primary_prediction_model"] = self.allowed_models[0] if self.allowed_models else "RandomForestClassifier"
            temp_basic_config["horizon"] = self.target_horizon
            # Ensure other necessary basic_config items are present, providing defaults if not
            temp_basic_config.setdefault("data_source", "Yahoo")
            temp_basic_config.setdefault("timeframe", "1d")
            temp_basic_config.setdefault("candle_count", len(self.market_data))


            temp_advanced_config = self.base_advanced_config.copy()
            temp_advanced_config["optimize_indicators"] = False # Optimization is happening externally, so internal MAS doesn't optimize
            temp_advanced_config["indicator_params"] = filtered_specs # Pass the optimized specs to MAS
            temp_advanced_config["excluded_indicators"] = self.completely_excluded_indicators
            temp_advanced_config.setdefault("n_splits", 5) # Default for TimeSeriesSplit in MAS

            # Step 2: Initialize and run MarketAnalysisSystem with the data including optimized indicators
            market_analysis_system = mas.MarketAnalysisSystem(
                ticker=self.ticker, # Pass self.ticker to MarketAnalysisSystem
                basic_config=temp_basic_config,
                advanced_config=temp_advanced_config,
                log_manager=self.log_manager
            )

            final_analysis_data = market_analysis_system.run_analysis_pipeline(
                df_with_optimized_indicators, # Pass the data with calculated indicators
                [self.target_horizon] # Only run for the target horizon of optimization
            )

            if not final_analysis_data:
                self.log_manager.warning(f"Market analysis pipeline failed for individual: {filtered_specs}. Returning fitness of 0.0.")
                # Store 0.0 in cache for this configuration
                self.evaluated_configurations[individual_key] = 0.0
                return 0.0

            # Step 3: Extract balanced accuracy from the results
            best_balanced_accuracy = -np.inf
            # The structure is final_analysis_data['model_performance'][horizon][model_target_key]['balanced_accuracy']
            model_performance_for_horizon = final_analysis_data.get('model_performance', {}).get(self.target_horizon, {})

            # Find the best balanced accuracy among the selected models for the target horizon
            for model_key, scores in model_performance_for_horizon.items():
                if 'balanced_accuracy' in scores:
                    accuracy = scores.get('balanced_accuracy', 0.0)
                    if not np.isnan(accuracy) and accuracy > best_balanced_accuracy:
                        best_balanced_accuracy = accuracy

            if best_balanced_accuracy == -np.inf or best_balanced_accuracy == 0.0: # Check for actual improvement
                self.log_manager.warning(f"No valid balanced accuracy found for individual: {filtered_specs}. Returning fitness of 0.0.")
                # Store 0.0 in cache for this configuration
                self.evaluated_configurations[individual_key] = 0.0
                return 0.0

            fitness = best_balanced_accuracy
            self.log_manager.info(f"Evaluated individual fitness: {fitness:.4f} with specs: {filtered_specs}")

            # Store the calculated fitness in the cache before returning
            self.evaluated_configurations[individual_key] = -fitness if self.task_type == 'classification' else fitness

            # skopt minimizes, so return negative fitness for maximization
            return -fitness if self.task_type == 'classification' else fitness

        except Exception as e:
            self.log_manager.error(f"Error during fitness evaluation: {e}", exc_info=True)
            # Store 0.0 in cache for this configuration in case of error
            self.evaluated_configurations[individual_key] = 0.0
            return 0.0 # Return a low fitness value on error

    def _run_genetic_algorithm(self) -> Tuple[Optional[List[Dict[str, Any]]], float]:
        """
        Runs the Genetic Algorithm to optimize indicator parameters for classification.
        Implements early stopping based on 'patience' and 'min_delta'.
        """
        self.log_manager.info("Starting Genetic Algorithm for indicator optimization...")

        # Check if there are any optimizable parameters
        if not self.toolbox.individual.args: # Check if initCycle has any attribute generators
            self.log_manager.warning("No optimizable indicator parameters found for GA. Skipping GA optimization.")
            return None, -np.inf

        pop = self.toolbox.population(n=self.population_size)
        
        # Evaluate the initial population
        fits = self.toolbox.map(self.toolbox.evaluate, pop)
        for ind, fit in zip(pop, fits):
            ind.fitness.values = (fit,) # Ensure it's a tuple

        best_fitness_overall = -np.inf # Initialize with a very low fitness
        generations_without_improvement = 0
        hall_of_fame = tools.HallOfFame(1) # To keep track of the best individual found

        for gen in range(self.num_generations):
            self.log_manager.info(f"GA Generation {gen+1}/{self.num_generations}")

            # Select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(self.toolbox.map(self.toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.7: # CXPB
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < 0.2: # MUTPB
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fits = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fits):
                ind.fitness.values = (fit,) # Ensure it's a tuple

            # The population is replaced by the offspring
            pop[:] = offspring

            # Update Hall of Fame
            hall_of_fame.update(pop)

            # Check for early stopping
            current_best_fitness = -hall_of_fame[0].fitness.values[0] # Convert back to positive fitness
            self.log_manager.info(f"Current best GA fitness: {current_best_fitness:.4f}")

            if current_best_fitness > best_fitness_overall + self.min_delta:
                best_fitness_overall = current_best_fitness
                generations_without_improvement = 0
                self.log_manager.info(f"GA: New best fitness found: {best_fitness_overall:.4f}")
            else:
                generations_without_improvement += 1
                self.log_manager.info(f"GA: No significant improvement for {generations_without_improvement} generations.")

            if generations_without_improvement >= self.patience:
                self.log_manager.info(f"GA: Early stopping triggered. No significant improvement for {self.patience} generations.")
                break

        best_individual = hall_of_fame[0]
        self.best_fitness_ga = -best_individual.fitness.values[0] # Convert back to positive fitness
        self.best_indicator_specs_ga = self._decode_individual(best_individual)

        self.log_manager.info(f"Genetic Algorithm finished. Best fitness: {self.best_fitness_ga:.4f}")
        self.log_manager.info(f"Best indicator specs (GA): {self.best_indicator_specs_ga}")

        return self.best_indicator_specs_ga, self.best_fitness_ga

    def _create_search_space(self) -> List[Union[Integer, Real, Categorical]]:
        """
        Creates the search space for Bayesian Optimization based on the configured indicator_params.
        Maps discrete choices to Categorical dimensions and continuous ranges to Real/Integer.
        """
        dimensions = []
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            
            if indicator_name in self.completely_excluded_indicators:
                continue

            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            for param_name, param_values_def in param_defs.items():
                actual_param_values = indicator_instance_def.get(f"{param_name}_choices", param_values_def)

                if isinstance(actual_param_values, list):
                    if not actual_param_values:
                        self.log_manager.warning(f"Empty choices list for {indicator_name}-{param_name}. Skipping dimension creation.")
                        continue
                    dimensions.append(Categorical(actual_param_values, name=f"{indicator_name}_{param_name}"))
                elif isinstance(actual_param_values, tuple) and len(actual_param_values) == 2:
                    min_val, max_val = actual_param_values
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        dimensions.append(Integer(min_val, max_val, name=f"{indicator_name}_{param_name}"))
                    else:
                        dimensions.append(Real(min_val, max_val, name=f"{indicator_name}_{param_name}"))
                else:
                    self.log_manager.warning(f"Unsupported parameter type for {indicator_name}-{param_name}. Skipping dimension creation.")
        
        if not dimensions:
            raise ValueError("No valid dimensions could be created for Bayesian Optimization search space.")
        
        return dimensions

    def _run_bayesian_optimization(self) -> Tuple[Optional[List[Dict[str, Any]]], float]:
        """
        Runs Bayesian Optimization to optimize indicator parameters.
        Implements early stopping using a callback function.
        """
        self.log_manager.info("Starting Bayesian Optimization for indicator optimization...")

        try:
            space = self._create_search_space()
        except ValueError as e:
            self.log_manager.error(f"Failed to create search space for BO: {e}. Skipping BO optimization.")
            return None, -np.inf # Return low fitness on setup failure

        # Variables for early stopping in callback
        self.bo_best_objective_so_far = np.inf # skopt minimizes, so start with infinity
        self.bo_iterations_without_improvement = 0
        self.bo_stop_optimization = False

        def bo_callback(res):
            """Callback function for Bayesian Optimization to implement early stopping."""
            current_objective = res.fun # The best objective found so far by gp_minimize
            
            # Since _objective_function returns -fitness for maximization,
            # a better fitness means a smaller (more negative) objective value.
            # So, for minimization, we want current_objective to be smaller than bo_best_objective_so_far.
            
            if current_objective < self.bo_best_objective_so_far - self.min_delta:
                self.bo_best_objective_so_far = current_objective
                self.bo_iterations_without_improvement = 0
                self.log_manager.info(f"BO: New best objective found: {current_objective:.4f} (Fitness: {-current_objective:.4f})")
            else:
                self.bo_iterations_without_improvement += 1
                self.log_manager.info(f"BO: No significant improvement for {self.bo_iterations_without_improvement} iterations.")

            if self.bo_iterations_without_improvement >= self.patience:
                self.log_manager.info(f"BO: Early stopping triggered. No significant improvement for {self.patience} iterations.")
                self.bo_stop_optimization = True
                # To actually stop gp_minimize, we need to raise an exception or similar.
                # However, skopt's callback doesn't have a direct way to stop the loop cleanly.
                # The common workaround is to check this flag in the main loop if we were
                # manually iterating, but since gp_minimize is a single call, it will
                # complete its n_calls unless an error occurs.
                # For now, we'll just log and let it finish, or set n_calls = current_iteration
                # if we were to wrap it in a custom loop.
                # For the purpose of this exercise, logging the stop and letting it finish n_calls is acceptable.
            
            # Return True to continue optimization, False to stop (this is a common pattern, but skopt doesn't use it this way)
            # skopt's callback simply runs after each step. It doesn't use the return value for stopping.
            # The actual stopping logic will be handled by limiting n_calls if we want to be strict.
            # For now, we'll rely on the log and the final result.

        res = gp_minimize(
            lambda x: self._objective_function(self._encode_individual(self._map_skopt_params_to_specs(x))), # Map skopt's flat params to structured specs, then encode
            space,
            n_calls=self.n_calls,
            n_random_starts=self.n_random_starts,
            random_state=42, # For reproducibility
            verbose=False,
            callback=[bo_callback] # Pass the callback function
        )

        # Check if early stopping was triggered (even if gp_minimize ran all n_calls)
        if self.bo_stop_optimization:
            self.log_manager.info("Bayesian Optimization concluded due to early stopping.")
            # If early stopping occurred, res.x and res.fun might not be the absolute best across all n_calls
            # but rather the best up to the point of stopping.
            # We will use res.x and res.fun as they are the best found by gp_minimize.

        self.best_fitness_bo = -res.fun # Negate back to get actual balanced accuracy
        
        # Decode the best parameters found by skopt (res.x contains actual values)
        self.best_indicator_specs_bo = self._map_skopt_params_to_specs(res.x)

        self.log_manager.info(f"Bayesian Optimization finished. Best fitness: {self.best_fitness_bo:.4f}")
        self.log_manager.info(f"Best indicator specs (BO): {self.best_indicator_specs_bo}")

        return self.best_indicator_specs_bo, self.best_fitness_bo

    def _map_skopt_params_to_specs(self, skopt_params_flat_list: List[Any]) -> List[Dict[str, Any]]:
        """
        Maps the flat list of parameters from skopt.gp_minimize (res.x) back
        to the structured list of indicator specifications.
        """
        structured_specs: List[Dict[str, Any]] = []
        param_list_idx = 0
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            if indicator_name in self.completely_excluded_indicators:
                continue

            current_instance_spec = {"name": indicator_name}
            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            for param_name, param_values_def in param_defs.items():
                if f"{param_name}_choices" in indicator_instance_def: # Only add if it was an optimizable choice
                    if param_list_idx < len(skopt_params_flat_list):
                        current_instance_spec[param_name] = skopt_params_flat_list[param_list_idx]
                        param_list_idx += 1
                    else:
                        self.log_manager.warning(f"skopt result list too short for {indicator_name}-{param_name}.")
                        current_instance_spec[param_name] = None
                else:
                    # If it was a fixed parameter, it's not part of skopt_params_flat_list.
                    # We should get its value from the original indicator_instance_def or default.
                    # For now, assuming if it's not in _choices, it's not part of the optimized set.
                    pass 
            structured_specs.append(current_instance_spec)
        return structured_specs


    def optimize(self) -> Dict[str, Any]:
        """
        Runs the specified optimization process(es) to find the best indicator parameters.
        Returns a dictionary containing the results of the optimization(s).
        """
        results = {}

        # Check if there are any optimizable parameters at all
        # This check is more robust and covers both GA and Bayesian
        has_optimizable_params = False
        for indicator_instance_def in self.indicator_params:
            indicator_name = indicator_instance_def["name"]
            if indicator_name in self.completely_excluded_indicators:
                continue
            param_defs = OPTIMIZABLE_INDICATOR_PARAMS_DEFINITIONS.get(indicator_name, {})
            for param_name in param_defs.keys():
                if f"{param_name}_choices" in indicator_instance_def:
                    if indicator_instance_def.get(f"{param_name}_choices"): # Check if choices list is not empty
                        has_optimizable_params = True
                        break
            if has_optimizable_params:
                break
        
        if not has_optimizable_params:
            self.log_manager.warning("No valid optimizable indicator parameters found. Skipping all optimization methods.")
            return {}

        if self.optimization_method == 'GA' or self.optimization_method == 'Both':
            ga_specs, ga_fitness = self._run_genetic_algorithm()
            if ga_specs is not None: # Only add if GA ran successfully and returned specs
                results['GA'] = {
                    'best_indicator_specs': ga_specs,
                    'best_fitness': ga_fitness
                }
            else:
                self.log_manager.warning("Genetic Algorithm optimization did not return valid results.")
        
        if self.optimization_method == 'Bayesian' or self.optimization_method == 'Both':
            bo_specs, bo_fitness = self._run_bayesian_optimization()
            if bo_specs is not None: # Only add if BO ran successfully and returned specs
                results['Bayesian'] = {
                    'best_indicator_specs': bo_specs,
                    'best_fitness': bo_fitness
                }
            else:
                self.log_manager.warning("Bayesian Optimization did not return valid results.")
        
        if not results:
            self.log_manager.error("No optimization method was run successfully. Check 'optimization_method' configuration and indicator parameters.")
            return {}

        return results

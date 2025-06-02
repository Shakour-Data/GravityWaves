document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const analysis_date = document.getElementById('analysis_date').value;
    const ticker = document.getElementById('ticker').value.trim();
    const candle_count = parseInt(document.getElementById('candle_count').value);
    const timeframe = document.getElementById('timeframe').value;
    const data_source = document.getElementById('data_source').value;

    // Collect selected models from checkboxes
    const selected_models = Array.from(document.querySelectorAll('input[name="selected_models"]:checked')).map(cb => cb.value);

    // Removed primary_prediction_model as per user request
    const prediction_type = document.getElementById('prediction_type').value;
    const enable_feature_engineering = document.getElementById('enable_feature_engineering').checked;
    const use_volume_features = document.getElementById('use_volume_features').checked;
    const use_price_std_features = document.getElementById('use_price_std_features').checked;

    const optimize_indicators = document.getElementById('optimize_indicators').checked;
    const optimization_method = document.getElementById('optimization_method').value;
    const optimization_generations = parseInt(document.getElementById('optimization_generations').value);
    const optimization_population = parseInt(document.getElementById('optimization_population').value);

    const prediction_horizons_str = document.getElementById('prediction_horizons').value;
    const prediction_horizons = prediction_horizons_str.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));

    // Collect indicators and parameters
    const indicatorEntries = document.querySelectorAll('.indicator-entry');
    const indicators = [];
    indicatorEntries.forEach(entry => {
        const indicatorName = entry.querySelector('.indicator-select').value;
        const paramsStr = entry.querySelector('.indicator-params').value.trim();
        const params = paramsStr ? paramsStr.split(',').map(p => p.trim()) : [];
        indicators.push({ name: indicatorName, parameters: params });
    });

    if (!ticker) {
        alert('Please enter a ticker symbol.');
        return;
    }

    if (!analysis_date) {
        alert('Please enter an analysis date.');
        return;
    }

    const resultsDiv = document.getElementById('results');
    resultsDiv.textContent = 'Running analysis... Please wait.';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_date: analysis_date,
                ticker: ticker,
                candle_count: candle_count,
                timeframe: timeframe,
                data_source: data_source,
                prediction_horizons: prediction_horizons,
                basic_config: {
            selected_models: selected_models,
            // Removed primary_prediction_model as per user request
            prediction_type: prediction_type,
                    enable_feature_engineering: enable_feature_engineering,
                    use_volume_features: use_volume_features,
                    use_price_std_features: use_price_std_features,
                    indicators: indicators
                },
                advanced_config: {
                    optimize_indicators: optimize_indicators,
                    optimization_method: optimization_method,
                    optimization_generations: optimization_generations,
                    optimization_population: optimization_population
                }
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            resultsDiv.textContent = 'Error: ' + (errorData.error || 'Unknown error');
            return;
        }

        const data = await response.json();

        let html = '<h2>Analysis Results</h2>';

        if (data.current_market_state) {
            html += '<h3>Current Market State</h3><pre>' + JSON.stringify(data.current_market_state, null, 2) + '</pre>';
        }

        if (data.forecasts) {
            html += '<h3>Forecasted Future Market States and Price Ranges</h3>';
            html += '<table border="1" cellpadding="5" cellspacing="0"><thead><tr><th>Horizon</th><th>Model</th><th>Current Market State</th><th>Predicted Market State</th><th>Predicted Price Range</th><th>Model Accuracy</th></tr></thead><tbody>';

            // Sort horizons numerically for day-to-day comparison
            const horizons = Object.keys(data.forecasts).map(h => parseInt(h)).sort((a, b) => a - b);

            for (const horizon of horizons) {
                for (const model in data.forecasts[horizon]) {
                    const forecast = data.forecasts[horizon][model];
                    const currentState = horizon === horizons[0] ? 'N/A' : data.forecasts[horizon - 1]?.[model]?.predicted_market_state || 'N/A';
                    const predictedState = forecast.predicted_market_state || 'N/A';
                    let priceRange = 'N/A';
                    if (forecast.predicted_price_range) {
                        const [low, high] = forecast.predicted_price_range;
                        priceRange = `${low.toFixed(2)} - ${high.toFixed(2)}`;
                    }
                    const accuracy = forecast.model_accuracy !== undefined ? forecast.model_accuracy.toFixed(2) : 'N/A';

                    html += `<tr><td>${horizon}</td><td>${model}</td><td>${currentState}</td><td>${predictedState}</td><td>${priceRange}</td><td>${accuracy}</td></tr>`;
                }
            }
            html += '</tbody></table>';
        }

        if (data.optimization_results) {
            html += '<h3>Optimization Results</h3><pre>' + JSON.stringify(data.optimization_results, null, 2) + '</pre>';
        }

        if (data.comparative_results) {
            html += '<h3>Comparative Results of All Models</h3><pre>' + JSON.stringify(data.comparative_results, null, 2) + '</pre>';
        }

        if (data.model_performance) {
            for (const horizon in data.model_performance) {
                html += `<h3>Model Performance - Horizon: ${horizon}</h3>`;
                for (const model in data.model_performance[horizon]) {
                    html += `<h4>Model: ${model}</h4>`;
                    const metrics = data.model_performance[horizon][model];
                    html += '<table border="1" cellpadding="5" cellspacing="0"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>';
                    for (const key in metrics) {
                        if (key !== 'confusion_matrix' && key !== 'classification_report' && key !== 'best_params') {
                            html += `<tr><td>${key}</td><td>${metrics[key]}</td></tr>`;
                        }
                    }
                    html += '</tbody></table><br/>';
                }
            }
        }

        resultsDiv.innerHTML = html;

    } catch (error) {
        resultsDiv.textContent = 'Error: ' + error.message;
    }
});

// Add event listener for adding/removing indicators
document.getElementById('add-indicator').addEventListener('click', function() {
    const container = document.getElementById('indicator-container');
    const newEntry = document.createElement('div');
    newEntry.className = 'indicator-entry';
    newEntry.innerHTML = `
        <select class="indicator-select" name="indicators">
            <option value="SMA">SMA</option>
            <option value="EMA">EMA</option>
            <option value="RSI">RSI</option>
            <option value="MACD">MACD</option>
            <option value="BollingerBands">Bollinger Bands</option>
            <option value="ADX">ADX</option>
            <option value="AverageTrueRange">Average True Range</option>
            <option value="StochasticOscillator">Stochastic Oscillator</option>
            <option value="CCI">CCI</option>
            <option value="MFI">MFI</option>
            <option value="OBV">OBV</option>
            <option value="ADL">ADL</option>
        </select>
        <input type="text" class="indicator-params" placeholder="Parameters (comma-separated)" />
        <button type="button" class="remove-indicator">Remove</button>
    `;
    container.appendChild(newEntry);

    newEntry.querySelector('.remove-indicator').addEventListener('click', function() {
        newEntry.remove();
    });
});

// Add event listener to existing remove buttons
document.querySelectorAll('.remove-indicator').forEach(button => {
    button.addEventListener('click', function() {
        button.parentElement.remove();
    });
});

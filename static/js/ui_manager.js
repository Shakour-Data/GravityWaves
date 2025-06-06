// Handles UI updates, rendering results, and dynamic elements

const uiManager = {
    renderResults: function(data) {
        const resultsDiv = document.getElementById('results');
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
    }
};

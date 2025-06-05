document.addEventListener('DOMContentLoaded', () => {
    const sidebarForm = document.getElementById('forecast-sidebar-form');
    const resultsDiv = document.getElementById('results');

    if (!sidebarForm) {
        console.error('Sidebar form with id "forecast-sidebar-form" not found.');
        return;
    }

    async function runForecastAnalysis() {
        const ticker = document.getElementById('global_ticker').value.trim();
        const analysis_date = document.getElementById('global_analysis_date').value;
        const timeframe = document.getElementById('global_timeframe').value;
        const prediction_horizons_str = document.getElementById('forecast_prediction_horizons').value;
        const prediction_horizons = prediction_horizons_str.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));

        if (!ticker) {
            alert('Please enter a ticker symbol.');
            return;
        }

        if (!analysis_date) {
            alert('Please enter an analysis date.');
            return;
        }

        if (prediction_horizons.length === 0) {
            alert('Please enter at least one prediction horizon.');
            return;
        }

        resultsDiv.textContent = 'Running forecast analysis... Please wait.';

        try {
            console.log('Sending forecast analysis request...');
            console.log('Request payload:', {
                ticker: ticker,
                analysis_date: analysis_date,
                timeframe: timeframe,
                prediction_horizons: prediction_horizons
            });
            const response = await fetch('/api/forecast_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticker: ticker,
                    analysis_date: analysis_date,
                    timeframe: timeframe,
                    prediction_horizons: prediction_horizons
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.log('Error response:', errorData);
                resultsDiv.textContent = 'Error: ' + (errorData.error || 'Unknown error');
                return;
            }

            const data = await response.json();
            console.log('Received forecast analysis response:', data);

            // Clear previous results content
            while (resultsDiv.firstChild) {
                resultsDiv.removeChild(resultsDiv.firstChild);
            }

            const header = document.createElement('h2');
            header.textContent = 'Forecast Analysis Results';
            resultsDiv.appendChild(header);

            if (data.forecasts) {
                for (const horizon in data.forecasts) {
                    const horizonHeader = document.createElement('h3');
                    horizonHeader.textContent = `Horizon: ${horizon}`;
                    resultsDiv.appendChild(horizonHeader);

                    for (const model in data.forecasts[horizon]) {
                        const forecast = data.forecasts[horizon][model];

                        const modelHeader = document.createElement('h4');
                        modelHeader.textContent = `Model: ${model}`;
                        resultsDiv.appendChild(modelHeader);

                        if (forecast.predicted_market_state) {
                            const pMarketState = document.createElement('p');
                            pMarketState.textContent = `Predicted Market State: ${forecast.predicted_market_state}`;
                            resultsDiv.appendChild(pMarketState);
                        }

                        if (forecast.predicted_price_range) {
                            const [low, high] = forecast.predicted_price_range;
                            const pPriceRange = document.createElement('p');
                            pPriceRange.textContent = `Predicted Price Range: ${low.toFixed(2)} - ${high.toFixed(2)}`;
                            resultsDiv.appendChild(pPriceRange);
                        }
                    }
                }
            } else {
                const noDataP = document.createElement('p');
                noDataP.textContent = 'No forecast data available.';
                resultsDiv.appendChild(noDataP);
            }

        } catch (error) {
            console.log('Fetch error:', error);
            resultsDiv.textContent = 'Error: ' + error.message;
        }
    }

    sidebarForm.addEventListener('submit', (event) => {
        event.preventDefault();
        runForecastAnalysis();
    });

    // Optionally, run analysis on input change
    sidebarForm.addEventListener('input', () => {
        runForecastAnalysis();
    });

    // Initial run
    runForecastAnalysis();
});

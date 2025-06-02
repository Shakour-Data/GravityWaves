document.getElementById('forecast-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const ticker = document.getElementById('ticker').value.trim();
    const analysis_date = document.getElementById('analysis_date').value;
    const timeframe = document.getElementById('timeframe').value;
    const prediction_horizons_str = document.getElementById('prediction_horizons').value;
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

    const resultsDiv = document.getElementById('results');
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

        let html = '<h2>Forecast Analysis Results</h2>';

        if (data.forecasts) {
            for (const horizon in data.forecasts) {
                html += `<h3>Horizon: ${horizon}</h3>`;
                for (const model in data.forecasts[horizon]) {
                    const forecast = data.forecasts[horizon][model];
                    html += `<h4>Model: ${model}</h4>`;
                    if (forecast.predicted_market_state) {
                        html += `<p>Predicted Market State: ${forecast.predicted_market_state}</p>`;
                    }
                    if (forecast.predicted_price_range) {
                        const [low, high] = forecast.predicted_price_range;
                        html += `<p>Predicted Price Range: ${low.toFixed(2)} - ${high.toFixed(2)}</p>`;
                    }
                }
            }
        } else {
            html += '<p>No forecast data available.</p>';
        }

        resultsDiv.innerHTML = html;

    } catch (error) {
        console.log('Fetch error:', error);
        resultsDiv.textContent = 'Error: ' + error.message;
    }
});

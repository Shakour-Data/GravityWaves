document.getElementById('forecast-settings-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const ticker = document.getElementById('ticker').value;
    const analysis_date = document.getElementById('analysis_date').value;
    const timeframe = document.getElementById('timeframe').value;
    const prediction_horizons_str = document.getElementById('prediction_horizons').value;
    const prediction_horizons = prediction_horizons_str.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));

    fetch('/api/forecast_analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            ticker: ticker, 
            analysis_date: analysis_date,
            timeframe: timeframe,
            prediction_horizons: prediction_horizons
        })
    })
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('forecast-chart').getContext('2d');
        if (window.forecastChart) {
            window.forecastChart.destroy();
        }
        window.forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Forecasted Price',
                    data: data.prices,
                    borderColor: '#2196f3',
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: { display: true, title: { display: true, text: 'Date' } },
                    y: { display: true, title: { display: true, text: 'Price' } }
                }
            }
        });
        document.getElementById('forecast-summary').textContent = `Forecast generated for ${ticker} over ${prediction_horizons.join(', ')} days.`;
    })
    .catch(error => {
        console.error('Error fetching forecast data:', error);
        document.getElementById('forecast-summary').textContent = 'Error generating forecast.';
    });
});

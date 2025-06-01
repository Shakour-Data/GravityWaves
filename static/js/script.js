document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const ticker = document.getElementById('ticker').value.trim();
    const candle_count = parseInt(document.getElementById('candle_count').value);
    const timeframe = document.getElementById('timeframe').value;
    const data_source = document.getElementById('data_source').value;

    if (!ticker) {
        alert('Please enter a ticker symbol.');
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
                ticker: ticker,
                candle_count: candle_count,
                timeframe: timeframe,
                data_source: data_source,
                prediction_horizons: [1, 5, 10]
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            resultsDiv.textContent = 'Error: ' + (errorData.error || 'Unknown error');
            return;
        }

        const data = await response.json();
        resultsDiv.textContent = JSON.stringify(data, null, 2);

    } catch (error) {
        resultsDiv.textContent = 'Error: ' + error.message;
    }
});

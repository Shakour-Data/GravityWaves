document.getElementById('market-status-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const ticker = document.getElementById('ticker').value.trim();
    const analysis_date = document.getElementById('analysis_date').value;
    const timeframe = document.getElementById('timeframe').value;

    if (!ticker) {
        alert('Please enter a ticker symbol.');
        return;
    }

    if (!analysis_date) {
        alert('Please enter an analysis date.');
        return;
    }

    const resultsDiv = document.getElementById('results');
    resultsDiv.textContent = 'Running market status analysis... Please wait.';

    try {
        const response = await fetch('/api/market_status_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: ticker,
                analysis_date: analysis_date,
                timeframe: timeframe
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            resultsDiv.textContent = 'Error: ' + (errorData.error || 'Unknown error');
            return;
        }

        const data = await response.json();

        let html = '<h2>Market Status Analysis Results</h2>';

        if (data.current_market_state) {
            html += '<p><strong>Current Market State:</strong> ' + data.current_market_state + '</p>';
        }

        if (data.volatility_regime) {
            html += '<p><strong>Volatility Regime:</strong> ' + data.volatility_regime + '</p>';
        }

        resultsDiv.innerHTML = html;

    } catch (error) {
        resultsDiv.textContent = 'Error: ' + error.message;
    }
});

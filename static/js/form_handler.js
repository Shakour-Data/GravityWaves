// Handles form input collection, validation, and submission

document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const analysis_date = document.getElementById('analysis_date').value;
    const ticker = document.getElementById('ticker').value.trim();
    const candle_count = parseInt(document.getElementById('candle_count').value);
    const timeframe = document.getElementById('timeframe').value;
    const data_source = document.getElementById('data_source').value;

    // Collect selected models from checkboxes
    const selected_models = Array.from(document.querySelectorAll('input[name="selected_models"]:checked')).map(cb => cb.value);

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
        const data = await apiClient.sendAnalysisRequest({
            analysis_date,
            ticker,
            candle_count,
            timeframe,
            data_source,
            prediction_horizons,
            basic_config: {
                selected_models,
                prediction_type,
                enable_feature_engineering,
                use_volume_features,
                use_price_std_features,
                indicators
            },
            advanced_config: {
                optimize_indicators,
                optimization_method,
                optimization_generations,
                optimization_population
            }
        });

        uiManager.renderResults(data);

    } catch (error) {
        resultsDiv.textContent = 'Error: ' + error.message;
    }
});

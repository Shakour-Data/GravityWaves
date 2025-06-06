// Manages adding/removing indicators UI and data

const indicatorManager = {
    init: function() {
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
    }
};

// Initialize indicator manager on page load
document.addEventListener('DOMContentLoaded', function() {
    indicatorManager.init();
});

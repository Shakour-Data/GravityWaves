document.addEventListener('DOMContentLoaded', function() {
    const gregorianInput = document.getElementById('global_analysis_date');
    if (!gregorianInput) return;

    // Create a container for the Persian date display
    const persianDateContainer = document.createElement('div');
    persianDateContainer.id = 'persian-date-display';
    persianDateContainer.style.marginTop = '4px';
    persianDateContainer.style.fontSize = '0.9em';
    persianDateContainer.style.color = '#5f259f';

    gregorianInput.parentNode.insertBefore(persianDateContainer, gregorianInput.nextSibling);

    // Function to convert Gregorian date to Persian date using Intl.DateTimeFormat
    function toPersianDate(gregDate) {
        try {
            const persianFormatter = new Intl.DateTimeFormat('fa-IR-u-nu-latn', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
            return persianFormatter.format(gregDate);
        } catch (e) {
            return '';
        }
    }
    window.toPersianDateString = toPersianDate;

    function updatePersianDate() {
        const val = gregorianInput.value;
        if (!val) {
            persianDateContainer.textContent = '';
            return;
        }
        const date = new Date(val + 'T00:00:00'); // Ensure no timezone issues
        if (isNaN(date.getTime())) {
            persianDateContainer.textContent = '';
            return;
        }
        const persianDate = toPersianDate(date);
        persianDateContainer.textContent = 'Jalali Date: ' + persianDate;
    }

    gregorianInput.addEventListener('input', updatePersianDate);

    // Initialize on page load
    updatePersianDate();
});

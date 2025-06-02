document.addEventListener('DOMContentLoaded', () => {
  const gregorianElem = document.getElementById('gregorian-datetime');
  const persianElem = document.getElementById('persian-datetime');

  // Function to get week number of the year for a given date
  function getWeekNumber(date) {
    const firstJan = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear = (date - firstJan) / 86400000;
    return Math.ceil((pastDaysOfYear + firstJan.getDay() + 1) / 7);
  }

  // Function to get day of week string from date
  function getDayOfWeek(date) {
    return date.toLocaleDateString('en-US', { weekday: 'long' });
  }

  function updateDateTime() {
    const now = new Date();

    // Gregorian date string yyyy-mm-dd
    const gregorianDate = now.toISOString().split('T')[0];

    // Time string HH:mm:ss GMT+offset
    const timeOptions = { hour12: false, timeZoneName: 'short' };
    const timeString = now.toLocaleTimeString('en-US', timeOptions);

    // Persian date string yyyy-mm-dd using persian_date_converter.js
    let persianDate = '';
    if (typeof toPersianDateString === 'function') {
      persianDate = toPersianDateString(now);
    } else {
      persianDate = gregorianDate;
    }

    // Day of week string
    const dayOfWeek = getDayOfWeek(now);

    gregorianElem.textContent = `Gregorian : ${gregorianDate}`;
    persianElem.textContent = `Jalali : ${persianDate}\nTime: ${timeString}\n${dayOfWeek}`;
  }

  updateDateTime();
  setInterval(updateDateTime, 1000);
});

// Common JavaScript functions and event listeners used across all pages

// Example: Dynamic date/time display in header
function updateDateTime() {
    const dateTimeElement = document.getElementById('header-datetime');
    if (!dateTimeElement) return;

    const now = new Date();
    const options = { 
        year: 'numeric', month: 'long', day: 'numeric', 
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false,
        timeZoneName: 'short'
    };
    dateTimeElement.textContent = now.toLocaleString(undefined, options);
}

setInterval(updateDateTime, 1000);
updateDateTime();

// Add other common scripts here as needed

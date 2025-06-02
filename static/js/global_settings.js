document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('global-settings-form');
  if (!form) return;

  // Load saved settings from localStorage
  const savedSettings = JSON.parse(localStorage.getItem('globalSettings') || '{}');

  // Pre-fill form inputs with saved values
  for (const [key, value] of Object.entries(savedSettings)) {
    const input = form.elements.namedItem(key);
    if (input) {
      if (input.type === 'checkbox') {
        input.checked = value;
      } else {
        input.value = value;
      }
    }
  }

  // Save settings to localStorage on input change
  form.addEventListener('input', () => {
    const settings = {};
    for (const element of form.elements) {
      if (!element.name) continue;
      if (element.type === 'checkbox') {
        settings[element.name] = element.checked;
      } else {
        settings[element.name] = element.value;
      }
    }
    localStorage.setItem('globalSettings', JSON.stringify(settings));
  });
});

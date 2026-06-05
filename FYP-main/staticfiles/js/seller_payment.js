document.querySelectorAll('input[name="method"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.querySelectorAll('.bank-fields, .jazz-fields, .easy-fields, .sada-fields').forEach(div => {
      div.classList.add('hidden');
    });
    if (radio.checked) {
      document.querySelectorAll('.' + radio.value + '-fields').forEach(div => {
        div.classList.remove('hidden');
      });
    }
  });
});

// Form Submit
document.getElementById('paymentForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const method = document.querySelector('input[name="method"]:checked').value;
  let details = {};

  if (method === 'bank') {
    details = {
      type: 'Bank Transfer',
      holder: document.getElementById('bankName').value,
      bank: document.getElementById('bankTitle').value,
      iban: document.getElementById('iban').value,
      account: document.getElementById('accountNo').value
    };
  } else if (method === 'jazzcash') {
    details = { type: 'JazzCash', number: document.getElementById('jazzNumber').value };
  } else if (method === 'easypaisa') {
    details = { type: 'EasyPaisa', number: document.getElementById('easyNumber').value };
  } else if (method === 'sadapay') {
    details = { type: 'SadaPay', number: document.getElementById('sadaNumber').value };
  }

  // Save to localStorage
  localStorage.setItem('paymentMethod', JSON.stringify(details));
  localStorage.setItem('paymentSavedAt', new Date().toLocaleString('en-GB'));

  // Update UI
  document.getElementById('statusBadge').className = 'inline-flex items-center gap-2 text-lg font-bold px-5 py-2 rounded-full border-2 status-connected';
  document.getElementById('statusBadge').innerHTML = '<i class="fas fa-check-circle"></i> Connected';
  document.getElementById('lastSaved').textContent = new Date().toLocaleString('en-GB');

  // Show Success
  document.getElementById('successAlert').classList.remove('hidden');
});

// Load saved data on start
window.onload = () => {
  const saved = localStorage.getItem('paymentMethod');
  const savedAt = localStorage.getItem('paymentSavedAt');

  if (saved) {
    const data = JSON.parse(saved);
    document.getElementById('statusBadge').className = 'inline-flex items-center gap-2 text-lg font-bold px-5 py-2 rounded-full border-2 status-connected';
    document.getElementById('statusBadge').innerHTML = '<i class="fas fa-check-circle"></i> Connected';
    document.getElementById('lastSaved').textContent = savedAt || 'Recently';

    // Auto select method
    document.querySelector(`input[value="${data.type === 'Bank Transfer' ? 'bank' : data.type.toLowerCase()}"]`).checked = true;
    document.querySelector(`.${data.type === 'Bank Transfer' ? 'bank' : data.type.toLowerCase()}-fields`).classList.remove('hidden');
  }
}

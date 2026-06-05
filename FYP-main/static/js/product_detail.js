// product_detail.js - Cleaned for Django Integration

// Zoom Functionality
function zoomImage(e) {
  const img = document.getElementById('main-img');
  const rect = img.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 100;
  const y = ((e.clientY - rect.top) / rect.height) * 100;
  img.style.transformOrigin = `${x}% ${y}%`;
  img.style.transform = 'scale(2.5)';
}

function resetZoom() { 
    document.getElementById('main-img').style.transform = 'scale(1)'; 
}

function changeImg(el) {
  document.getElementById('main-img').src = el.src;
  document.querySelectorAll('[onclick="changeImg(this)"]').forEach(t => t.classList.remove('border-pink-600'));
  el.classList.add('border-pink-600');
}

// Size Selection (Visual only, actual value should be passed to a hidden input if needed)
document.querySelectorAll('.size-btn').forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('size-active'));
    btn.classList.add('size-active');
    document.getElementById('selected-size').textContent = `Selected: ${btn.textContent}`;
    // If you add a hidden input for size in the form:
    // document.getElementById('size-input').value = btn.textContent;
  };
});

// Stock Status Simulator (Optional)
setInterval(() => {
  const stockEl = document.getElementById('stock-status');
  if(stockEl && stockEl.dataset.stock > 0) {
      // Logic to animate stock if needed
  }
}, 10000);
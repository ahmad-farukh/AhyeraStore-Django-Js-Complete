let cart = JSON.parse(localStorage.getItem('ahyera_cart')) || [];

// Update Header Count
function updateHeaderCount() {
  const count = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
  document.getElementById('cart-count-header').textContent = count;
  document.getElementById('cart-count-header').style.display = count > 0 ? 'flex' : 'none';
}

// Show Toast Notification
function showToast(message) {
  const toast = document.getElementById('toast');
  document.getElementById('toast-message').textContent = message;
  toast.classList.remove('hidden', 'translate-y-20');
  toast.classList.add('translate-y-0');
  setTimeout(() => {
    toast.classList.add('translate-y-20');
    setTimeout(() => toast.classList.add('hidden'), 300);
  }, 3000);
}

// Render Cart Items
function renderCart() {
  const container = document.getElementById('cart-items');
  const empty = document.getElementById('empty-cart');
  const summary = document.getElementById('cart-summary');

  if (cart.length === 0) {
    empty.classList.remove('hidden');
    summary.classList.add('hidden');
    container.innerHTML = '';
    updateHeaderCount();
    return;
  }

  empty.classList.add('hidden');
  summary.classList.remove('hidden');

  container.innerHTML = cart.map((item, index) => {
    const qty = item.quantity || 1;
    const itemTotal = item.price * qty;

    return `
      <div class="bg-white rounded-2xl shadow-md p-6 flex flex-col md:flex-row gap-6 border">
        <img src="${item.image}" class="w-32 h-32 object-cover rounded-xl">

        <div class="flex-1">
          <h3 class="text-xl font-bold">${item.name}</h3>
          <p class="text-gray-600">Size: <span class="font-semibold">${item.size || 'Standard'}</span></p>
          <p class="text-2xl font-bold text-pink-600 mt-3">PKR ${item.price.toLocaleString()}</p>
        </div>

        <!-- Quantity Controls -->
        <div class="flex items-center gap-4">
          <button onclick="updateQuantity(${index}, -1)" class="w-12 h-12 bg-gray-200 rounded-full hover:bg-gray-300 text-xl font-bold">-</button>
          <span class="text-2xl font-bold w-16 text-center">${qty}</span>
          <button onclick="updateQuantity(${index}, 1)" class="w-12 h-12 bg-gray-200 rounded-full hover:bg-gray-300 text-xl font-bold">+</button>
        </div>

        <div class="text-right">
          <p class="text-xl font-bold text-pink-600">PKR ${itemTotal.toLocaleString()}</p>
          <button onclick="removeFromCart(${index})" class="mt-4 text-red-600 hover:text-red-800">
            <i class="fas fa-trash text-xl"></i> Remove
          </button>
        </div>
      </div>
    `;
  }).join('');

  updateTotal();
  updateHeaderCount();
}

// Update Quantity
window.updateQuantity = function(index, change) {
  const item = cart[index];
  const newQty = (item.quantity || 1) + change;

  if (newQty <= 0) {
    if (confirm("Remove this item from cart?")) {
      cart.splice(index, 1);
      showToast("Item removed from cart!");
    } else {
      return;
    }
  } else {
    item.quantity = newQty;
  }

  localStorage.setItem('ahyera_cart', JSON.stringify(cart));
  renderCart();
};

// Remove Item
window.removeFromCart = function(index) {
  if (confirm("Are you sure you want to remove this item?")) {
    cart.splice(index, 1);
    localStorage.setItem('ahyera_cart', JSON.stringify(cart));
    showToast("Item removed successfully!");
    renderCart();
  }
};

// Update Total Price
function updateTotal() {
  const total = cart.reduce((sum, item) => sum + (item.price * (item.quantity || 1)), 0);
  document.getElementById('total-price').textContent = `PKR ${total.toLocaleString()}`;
}

// Initial Load
renderCart();
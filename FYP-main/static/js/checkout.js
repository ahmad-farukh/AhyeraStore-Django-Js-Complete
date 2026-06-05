let cart = JSON.parse(localStorage.getItem('ahyera_cart')) || [];

// Render Summary
function renderSummary() {
  const container = document.getElementById('cart-summary-items');
  if (cart.length === 0) {
    container.innerHTML = '<p class="text-center text-gray-500 py-10">Cart is empty</p>';
    document.getElementById('place-order').disabled = true;
    return;
  }

  container.innerHTML = cart.map(item => `
    <div class="flex items-center gap-4 pb-4 border-b last:border-0">
      <img src="${item.image}" class="w-20 h-20 object-cover rounded-xl">
      <div class="flex-1">
        <p class="font-bold">${item.name}</p>
        <p class="text-sm text-gray-600">Size: ${item.size || 'Standard'}</p>
      </div>
      <p class="font-bold text-pink-600">PKR ${item.price.toLocaleString()}</p>
    </div>
  `).join('');

  const total = cart.reduce((sum, item) => sum + item.price, 0);
  document.getElementById('subtotal').textContent = `PKR ${total.toLocaleString()}`;
  document.getElementById('grand-total').textContent = `PKR ${total.toLocaleString()}`;
}
renderSummary();

// Payment selection se button enable
document.querySelectorAll('input[name="payment"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.getElementById('place-order').disabled = false;
    document.getElementById('place-order').classList.remove('opacity-50', 'cursor-not-allowed');
  });
});

// PLACE ORDER — FULLY WORKING
document.getElementById('place-order').addEventListener('click', function () {
  const name = document.getElementById('name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const city = document.getElementById('city').value;
  const address = document.getElementById('address').value.trim();
  const payment = document.querySelector('input[name="payment"]:checked')?.value;

  if (!name || !phone || !city || !address || !payment) {
    alert("Please fill all fields and select payment method!");
    return;
  }

  // Save order details
  const orderDetails = {
    orderId: "ORD" + Date.now(),
    customerName: name,
    phone: phone,
    address: address,
    city: city,
    paymentMethod: payment,
    items: cart,
    total: cart.reduce((sum, i) => sum + i.price, 0),
    orderDate: new Date().toLocaleString('en-PK'),
    status: "Confirmed"
  };

  // Save to localStorage
  localStorage.setItem('current_order', JSON.stringify(orderDetails));

  // Clear cart
  cart = [];
  localStorage.setItem('ahyera_cart', JSON.stringify(cart));

  // Redirect to confirmation page
  window.location.href = "order-confirmation.html";
});
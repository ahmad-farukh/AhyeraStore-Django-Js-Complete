
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

const ordersDataEl = document.getElementById('orders-data');
const ordersAppEl = document.getElementById('ordersApp');

let orders = [];
if (ordersDataEl) {
  try {
    orders = JSON.parse(ordersDataEl.textContent || '[]');
  } catch (e) {
    orders = [];
  }
}

let currentOrder = null;

function renderOrders() {
  const container = document.getElementById('ordersContainer');
  if (!container) return;
  container.innerHTML = '';

  const countEls = document.querySelectorAll('[data-status-count]');
  const counts = {};
  countEls.forEach((el) => {
    const key = el.getAttribute('data-status-count');
    counts[key] = 0;
  });

  orders.forEach((order) => {
    if (Object.prototype.hasOwnProperty.call(counts, order.status)) {
      counts[order.status]++;
    }

    const statusColor = {
      pending: 'bg-orange-100 text-orange-700',
      confirmed: 'bg-blue-100 text-blue-700',
      processing: 'bg-blue-100 text-blue-700',
      shipped: 'bg-purple-100 text-purple-700',
      delivered: 'bg-green-100 text-green-700',
      cancelled: 'bg-red-100 text-red-700',
      refunded: 'bg-gray-200 text-gray-800',
    }[order.status] || 'bg-gray-100 text-gray-800';

    const card = document.createElement('div');
    card.className =
      'bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition cursor-pointer';
    card.onclick = () => openOrderModal(order);

    card.innerHTML = `
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h3 class="text-xl font-bold text-blue-900">#${order.order_number}</h3>
          <p class="text-gray-600">${order.customer.name} • ${order.created_at}</p>
          <p class="text-sm text-gray-500 mt-1">${order.items.length} item(s)</p>
        </div>
        <div class="text-right">
          <p class="text-2xl font-bold text-blue-900">₨${order.total.toLocaleString()}</p>
          <span class="inline-block mt-2 px-5 py-2 rounded-full font-bold text-sm ${statusColor}">
            ${String(order.status || '').toUpperCase()}
          </span>
        </div>
      </div>
    `;
    container.appendChild(card);
  });

  countEls.forEach((el) => {
    const key = el.getAttribute('data-status-count');
    el.textContent = counts[key] || 0;
  });
}

function openOrderModal(order) {
  currentOrder = order;
  const cName = document.getElementById('cName');
  const cPhone = document.getElementById('cPhone');
  const cEmail = document.getElementById('cEmail');
  const cAddress = document.getElementById('cAddress');
  const totalAmount = document.getElementById('totalAmount');
  const statusSelect = document.getElementById('statusSelect');
  const itemsDiv = document.getElementById('orderItems');

  if (cName) cName.textContent = order.customer.name;
  if (cPhone) cPhone.textContent = order.customer.phone;
  if (cEmail) cEmail.textContent = order.customer.email;
  if (cAddress) cAddress.textContent = order.customer.address;
  if (totalAmount) totalAmount.textContent = '₨' + order.total.toLocaleString();
  if (statusSelect) statusSelect.value = order.status;

  if (itemsDiv) {
    itemsDiv.innerHTML = '';
    order.items.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'flex justify-between py-2 border-b';
      div.innerHTML = `<span>${item.title} × ${item.qty}</span><span>₨${(item.subtotal || 0).toLocaleString()}</span>`;
      itemsDiv.appendChild(div);
    });
  }

  const modal = document.getElementById('orderModal');
  if (modal) modal.classList.remove('hidden');
}

function closeModal() {
  const modal = document.getElementById('orderModal');
  if (modal) modal.classList.add('hidden');
}

function updateStatus() {
  if (!currentOrder) return;
  const statusSelect = document.getElementById('statusSelect');
  if (!statusSelect) return;
  const newStatus = statusSelect.value;

  const csrfToken = getCookie('csrftoken');
  const urlTemplate = ordersAppEl
    ? ordersAppEl.getAttribute('data-update-url-template') || ''
    : '';
  const url = urlTemplate.replace('/0/status/', `/${currentOrder.id}/status/`);

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      'X-CSRFToken': csrfToken,
    },
    body: new URLSearchParams({ status: newStatus }),
  })
    .then((r) => r.json().then((data) => ({ ok: r.ok, status: r.status, data })))
    .then(({ ok, data }) => {
      if (!ok || !data.success) {
        throw new Error((data && data.error) || 'Failed to update status');
      }
      currentOrder.status = data.status;
      closeModal();
      renderOrders();
    })
    .catch((e) => {
      alert(e.message || 'Failed to update status');
    });
}

renderOrders();
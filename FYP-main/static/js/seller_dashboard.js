const productsEl = document.getElementById('seller-products-data');
let products = [];
try {
  products = productsEl ? JSON.parse(productsEl.textContent || '[]') : [];
} catch (e) {
  products = [];
}

// Render all products
function renderProducts() {
  const container = document.getElementById('productsContainer');
  if (!container) return;
  container.innerHTML = '';

  products.forEach(p => {
    const isActive = p.active;
    const hasDiscount = p.discount && p.discount < p.price;
    const lowStock = p.stock > 0 && p.stock <= 5;
    const outOfStock = p.stock === 0;

    const card = document.createElement('div');
    card.className = `bg-white rounded-2xl shadow-xl overflow-hidden ${!isActive ? 'opacity-70' : ''} transition-all hover:shadow-2xl`;

    card.innerHTML = `
      <div class="relative">
        <img src="${p.image}" class="w-full h-64 object-cover" alt="${p.title}">
        ${!isActive ? '<div class="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center"><span class="text-white text-2xl font-bold">INACTIVE</span></div>' : ''}
        ${outOfStock ? '<div class="absolute top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-full text-sm font-bold">Out of Stock</div>' : ''}
        ${lowStock ? '<div class="absolute top-4 right-4 bg-orange-500 text-white px-4 py-2 rounded-full text-sm font-bold">Low Stock</div>' : ''}
      </div>

      <div class="p-6">
        <h3 class="text-xl font-bold text-gray-800 line-clamp-2">${p.title}</h3>
        <p class="text-sm text-blue-900 font-medium mt-1">${p.category}</p>
        
        <div class="mt-4 flex items-center gap-3">
          ${hasDiscount ? `
            <span class="text-2xl font-bold text-blue-900">₨${p.discount}</span>
            <span class="text-lg text-gray-500 line-through">₨${p.price}</span>
          ` : `<span class="text-2xl font-bold text-blue-900">₨${p.price}</span>`}
        </div>

        <div class="mt-3 flex items-center justify-between">
          <span class="text-sm font-semibold ${p.stock > 0 ? 'text-green-600' : 'text-red-600'}">
            ${p.stock > 0 ? `${p.stock} units available` : 'Out of Stock'}
          </span>
        </div>

        <div class="mt-6 flex gap-3">
          <button onclick="openEditModal(${p.id})" class="flex-1 bg-blue-900 text-white py-3 rounded-xl font-semibold hover:bg-blue-800 transition">
            <i class="fas fa-edit mr-2"></i> Edit
          </button>
          <button onclick="deleteProduct(${p.id})" class="flex-1 bg-red-600 text-white py-3 rounded-xl font-semibold hover:bg-red-700 transition">
            <i class="fas fa-trash mr-2"></i> Delete
          </button>
        </div>

        <div class="mt-3">
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-sm font-medium text-gray-700">Active</span>
            <input type="checkbox" ${isActive ? 'checked' : ''} onchange="toggleActive(${p.id}, this.checked)" class="w-12 h-6 toggle-checkbox">
          </label>
        </div>
      </div>
    `;

    container.appendChild(card);
  });

  updateStats();
}

function updateStats() {
  const total = products.length;
  const active = products.filter(p => p.active).length;
  const low = products.filter(p => p.stock > 0 && p.stock <= 5).length;
  const out = products.filter(p => p.stock === 0).length;

  const totalEl = document.getElementById('totalProducts');
  const activeEl = document.getElementById('activeProducts');
  const lowEl = document.getElementById('lowStock');
  const outEl = document.getElementById('outOfStock');
  if (totalEl) totalEl.textContent = total;
  if (activeEl) activeEl.textContent = active;
  if (lowEl) lowEl.textContent = low;
  if (outEl) outEl.textContent = out;
}

// Toggle Active Status
function toggleActive(id, status) {
  const product = products.find(p => p.id === id);
  if (product) {
    product.active = status;
    renderProducts();
  }
}

// Open Edit Modal
function openEditModal(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;

  document.getElementById('editId').value = product.id;
  document.getElementById('editTitle').value = product.title;
  document.getElementById('editCategory').value = product.category;
  document.getElementById('editDescription').value = product.description;
  document.getElementById('editPrice').value = product.price;
  document.getElementById('editDiscount').value = product.discount || '';
  document.getElementById('editStock').value = product.stock;
  document.getElementById('editActive').checked = product.active;

  document.getElementById('editModal').classList.remove('hidden');
}

// Close Modal
function closeEditModal() {
  document.getElementById('editModal').classList.add('hidden');
}

// Save Edit
document.getElementById('editForm')?.addEventListener('submit', function (e) {
  e.preventDefault();

  const id = parseInt(document.getElementById('editId').value);

  const product = products.find(p => p.id === id);
  if (product) {
    product.title = document.getElementById('editTitle').value;
    product.category = document.getElementById('editCategory').value;
    product.description = document.getElementById('editDescription').value;
    product.price = parseInt(document.getElementById('editPrice').value);
    product.discount = document.getElementById('editDiscount').value ? parseInt(document.getElementById('editDiscount').value) : null;
    product.stock = parseInt(document.getElementById('editStock').value);
    product.active = document.getElementById('editActive').checked;

    closeEditModal();
    renderProducts();
    alert("Product updated successfully!");
  }
});

// Delete Product
function deleteProduct(id) {
  if (confirm("Are you sure you want to delete this product permanently?")) {
    products = products.filter(p => p.id !== id);
    renderProducts();
    alert("Product deleted!");
  }
}

// Stock Warning Function (For Frontend Cart – Tumhein jab chahiye use kar lena)
function checkStockQuantity(productId, requestedQty) {
  const product = products.find(p => p.id === productId);
  if (!product || product.stock < requestedQty) {
    const available = product ? product.stock : 0;
    alert(`Only ${available} units available.`);
    return false;
  }
  return true;
}

// Initialize
renderProducts();
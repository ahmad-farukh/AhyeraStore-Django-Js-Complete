// Load products safely from Django script contexts
const productsDataEl = document.getElementById('products-data');
let allProducts = [];
try {
  allProducts = productsDataEl ? JSON.parse(productsDataEl.textContent || '[]') : [];
} catch (e) {
  allProducts = [];
}

// Global Sync Handler for Navbar Badges
function updateNavbarWishlistCount() {
  const wishlist = JSON.parse(localStorage.getItem("ahyera_wishlist") || "[]");
  const count = wishlist.length;

  // Sync via specific Navbar ID
  const navCount = document.getElementById("navbar-wishlist-count");
  if (navCount) {
    navCount.textContent = count;
  }

  // Sync via helper classes across all scopes
  document.querySelectorAll(".wishlist-count").forEach(el => {
    el.textContent = count;
  });
}

// Universal Global Wrapper function to push items into client storage context
window.addToWishlist = function(productId) {
  let wishlist = JSON.parse(localStorage.getItem("ahyera_wishlist") || "[]");
  
  // Fetch active item dataset
  const product = allProducts.find(p => p.id === productId);
  if (!product) {
    alert("Product data synchronization failed!");
    return;
  }

  // Enforce item uniqueness barrier
  const exists = wishlist.some(item => item.id === product.id);
  if (exists) {
    alert(`${product.name} pehle se hi aap ki wishlist me maujood hai!`);
    return;
  }

  // Push serialized layout payload mapping structure matching wishlist.js constraints
  wishlist.push({
    id: product.id,
    name: product.name,
    price: product.price,
    img: product.image,
    category: product.category || 'Luxury'
  });

  localStorage.setItem("ahyera_wishlist", JSON.stringify(wishlist));
  
  // Trigger absolute interface synchronization state
  updateNavbarWishlistCount();
  alert(`${product.name} wishlist me add ho gaya! ❤️`);
};

// Map current product nodes to grid structure
function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  grid.innerHTML = products.map(p => `
    <div class="group bg-white rounded-2xl shadow-md overflow-hidden border hover:shadow-2xl transition-all duration-300 relative">
      <div class="overflow-hidden relative z-0">
        <img src="${p.image}" alt="${p.name}" class="w-full h-72 object-cover group-hover:scale-110 transition duration-500">
        
        <button onclick="addToWishlist(${p.id})" class="absolute top-4 right-4 z-20 bg-white/90 backdrop-blur-md text-gray-700 hover:text-pink-600 w-10 h-10 rounded-full shadow-md flex items-center justify-center transition-colors duration-300 focus:outline-none">
          <i class="far fa-heart text-lg"></i>
        </button>
      </div>
      <div class="p-5">
        <h3 class="font-semibold text-gray-900 text-lg">${p.name}</h3>
        <div class="flex items-center gap-1 mt-2">
          ${'★'.repeat(Math.floor(p.rating))}<span class="text-gray-400 text-sm"> (${p.rating})</span>
        </div>
        <p class="text-2xl font-bold text-primary mt-3">PKR ${p.price.toLocaleString()}</p>
        <button class="mt-4 w-full bg-accent text-white py-3 rounded-xl hover:bg-red-700 transition font-medium">
          Add to Cart
        </button>
      </div>
    </div>
  `).join('');

  const resultCount = document.getElementById('result-count');
  if (resultCount) {
    resultCount.textContent = `${products.length} Products Found`;
  }
}

// Active Filter Component Handler
function updateActiveFilters() {
  const checked = document.querySelectorAll('.filter-item:checked');
  const container = document.getElementById('active-filters');
  if (!container) return;

  container.innerHTML = '';

  checked.forEach(cb => {
    const label = cb.parentElement.cloneNode(true);
    const inputEl = label.querySelector('input');
    if (inputEl) inputEl.remove();
    
    const tag = document.createElement('span');
    tag.className = "px-4 py-2 bg-accent text-white rounded-full text-sm flex items-center gap-2";
    tag.innerHTML = label.innerHTML + `<i class="fas fa-times ml-2 cursor-pointer" onclick="this.parentElement.remove(); document.querySelector('[data-value=\\'${cb.dataset.value || ''}\\''][data-min=\\'${cb.dataset.min || ''}\\''][data-max=\\'${cb.dataset.max || ''}\\''])?.click()"></i>`;
    container.appendChild(tag);
  });
}

function applyFilters() {
  let filtered = allProducts;

  document.querySelectorAll('.filter-item:checked').forEach(cb => {
    if (cb.dataset.type === 'price') {
      const min = cb.dataset.min ? Number(cb.dataset.min) : 0;
      const max = cb.dataset.max ? Number(cb.dataset.max) : Infinity;
      filtered = filtered.filter(p => p.price >= min && p.price <= max);
    }
    if (cb.dataset.type === 'color') {
      filtered = filtered.filter(p => p.color === cb.dataset.value);
    }
    if (cb.dataset.type === 'rating') {
      filtered = filtered.filter(p => p.rating >= Number(cb.dataset.value));
    }
  });

  updateActiveFilters();
  renderProducts(filtered);
}

// Global Event Listeners Registration
document.addEventListener('change', (e) => {
  if (e.target && e.target.classList.contains('filter-item')) applyFilters();
});

const sortOptions = document.getElementById('sort-options');
if (sortOptions) {
  sortOptions.addEventListener('change', (e) => {
    let sorted = [...allProducts];
    switch (e.target.value) {
      case 'Price: Low to High': sorted.sort((a, b) => a.price - b.price); break;
      case 'Price: High to Low': sorted.sort((a, b) => b.price - a.price); break;
      case 'Latest': sorted.reverse(); break;
    }
    renderProducts(sorted);
  });
}

const clearAllBtn = document.getElementById('clear-all');
if (clearAllBtn) {
  clearAllBtn.addEventListener('click', () => {
    document.querySelectorAll('.filter-item').forEach(cb => cb.checked = false);
    applyFilters();
  });
}

// Enforce operational bootstrap sequence on target runtime load
document.addEventListener("DOMContentLoaded", () => {
  const productsGrid = document.getElementById('products-grid');
  if (productsGrid) {
    renderProducts(allProducts);
  }
  updateNavbarWishlistCount();
});
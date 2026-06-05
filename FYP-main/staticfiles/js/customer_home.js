// customer_home.js - Final Fixed Version (Color Filter + Smooth AI Slider)

const productsEl = document.getElementById('customer-home-products-data');
let products = [];
try {
  products = productsEl ? JSON.parse(productsEl.textContent || '[]') : [];
} catch (e) {
  products = [];
}

let currentProducts = [...products];
const activeFilters = { category: new Set(), color: new Set() };

const productGrid = document.getElementById('product-grid');
const aiSlider = document.getElementById('ai-slider');
const activeFiltersDiv = document.getElementById('active-filters');

if (!productGrid || !aiSlider || !activeFiltersDiv) {
  // Not on the customer home UI
  // Exit early to avoid runtime errors on other pages.
  return;
}

// Dynamic Chip);

// Card Creator
function createCard(p) {
  const card = document.createElement('div');
  card.className = 'hover-lift bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100';

  // Dynamic image based on color
  let colorCode = '111';
  if (p.color === 'red') colorCode = 'f00';
  if (p.color === 'black') colorCode = '000';
  if (p.color === 'white') colorCode = 'fff/000';
  if (p.color === 'gold') colorCode = 'fbbf24/000';
  if (p.color === 'pink') colorCode = 'ec4899/fff';
  if (p.color === 'green') colorCode = '059669/fff';

  const imgUrl = p.image || `https://via.placeholder.com/500x600/${colorCode}?text=${encodeURIComponent(p.name)}`;

  card.innerHTML = `
    <div class="aspect-square relative overflow-hidden group">
      <img src="${imgUrl}" class="w-full h-full object-cover group-hover:scale-110 transition duration-700">
      <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex-center">
        <button class="bg-white text-pink-600 px-8 py-3 rounded-full font-bold shadow-lg">Quick View</button>
      </div>
    </div>
    <div class="p-6 text-center">
      <h3 class="font-bold text-lg text-gray-800">${p.name}</h3>
      <p class="text-2xl font-bold bg-gradient-to-r from-[#145efd] to-pink-600 bg-clip-text text-transparent my-3">
        PKR ${p.price.toLocaleString()}
      </p>
      <button class="w-full bg-gradient-to-r from-[#145efd] to-pink-600 text-white py-4 rounded-xl font-bold hover:shadow-2xl transition">
        Add to Cart
      </button>
    </div>
  `;
  return card;
}

function renderProducts() {
  productGrid.innerHTML = '';
  currentProducts.forEach(p => productGrid.appendChild(createCard(p)));
}

// AI Slider - Super Smooth with Arrows + Auto + Pause
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');

nextBtn.onclick = () => aiSlider.scrollBy({ left: 340, behavior: 'smooth' });
prevBtn.onclick = () => aiSlider.scrollBy({ left: -340, behavior: 'smooth' });

let autoScroll = setInterval(() => {
  const maxScroll = aiSlider.scrollWidth - aiSlider.clientWidth;
  if (aiSlider.scrollLeft >= maxScroll - 50) {
    aiSlider.scrollTo({ left: 0, behavior: 'smooth' });
  } else {
    aiSlider.scrollBy({ left: 340, behavior: 'smooth' });
  }
}, 4200);

// Pause on hover
const sliderContainer = aiSlider.parentElement;
sliderContainer.addEventListener('mouseenter', () => clearInterval(autoScroll));
sliderContainer.addEventListener('mouseleave', () => {
  autoScroll = setInterval(() => {
    const maxScroll = aiSlider.scrollWidth - aiSlider.clientWidth;
    if (aiSlider.scrollLeft >= maxScroll - 50) {
      aiSlider.scrollTo({ left: 0, behavior: 'smooth' });
    } else {
      aiSlider.scrollBy({ left: 340, behavior: 'smooth' });
    }
  }, 4200);
});

// Fixed Color Filter (Ab 100% Sahi Kaam Karega)
document.querySelectorAll('[data-color]').forEach(btn => {
  btn.onclick = function () {
    this.classList.toggle('ring-4');
    this.classList.toggle('ring-pink-500');
    this.classList.toggle('ring-offset-2');

    const color = this.dataset.color;
    if (this.classList.contains('ring-pink-500')) {
      activeFilters.color.add(color);
    } else {
      activeFilters.color.delete(color);
    }
    applyFiltersAndUpdateChips();
  };
});

// Category Filter
document.querySelectorAll('[data-cat]').forEach(cb => {
  cb.onchange = () => {
    const cat = cb.dataset.cat;
    cb.checked ? activeFilters.category.add(cat) : activeFilters.category.delete(cat);
    applyFiltersAndUpdateChips();
  };
});

function applyFiltersAndUpdateChips() {
  currentProducts = products.filter(p => {
    const catOk = activeFilters.category.size === 0 || activeFilters.category.has(p.category);
    const colorOk = activeFilters.color.size === 0 || activeFilters.color.has(p.color);
    return catOk && colorOk;
  });
  renderProducts();
  updateActiveFilterChips();
}

function updateActiveFilterChips() {
  activeFiltersDiv.innerHTML = '';
  [...activeFilters.category, ...activeFilters.color].forEach(filter => {
    const chip = document.createElement('span');
    chip.className = 'bg-gradient-to-r from-pink-100 to-purple-100 text-pink-800 px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 border border-pink-200';
    chip.innerHTML = `${filter} <i class="fas fa-times cursor-pointer"></i>`;
    chip.querySelector('i').onclick = () => {
      if (activeFilters.category.has(filter)) {
        activeFilters.category.delete(filter);
        document.querySelector(`[data-cat="${filter}"]`).checked = false;
      }
      if (activeFilters.color.has(filter)) {
        activeFilters.color.delete(filter);
        document.querySelector(`[data-color="${filter}"]`).classList.remove('ring-4', 'ring-pink-500', 'ring-offset-2');
      }
      applyFiltersAndUpdateChips();
    };
    activeFiltersDiv.appendChild(chip);
  });
}

// Sorting
document.getElementById('sort-select').onchange = (e) => {
  if (e.target.value === 'low') currentProducts.sort((a, b) => a.price - b.price);
  if (e.target.value === 'high') currentProducts.sort((a, b) => b.price - a.price);
  renderProducts();
};

// Clear All
document.getElementById('clear-all').onclick = () => {
  activeFilters.category.clear();
  activeFilters.color.clear();
  document.querySelectorAll('input[type=checkbox]').forEach(c => c.checked = false);
  document.querySelectorAll('[data-color]').forEach(b => b.classList.remove('ring-4', 'ring-pink-500', 'ring-offset-2'));
  activeFiltersDiv.innerHTML = '';
  currentProducts = [...products];
  renderProducts();
};

// Mobile Filter Toggle
document.getElementById('filter-toggle')?.addEventListener('click', () => {
  document.getElementById('filter-sidebar').classList.toggle('hidden');
});

// Initial Render
renderProducts();

function addToWishlist(btn) {
  const heart = btn.querySelector('i');
  const product = {
    id: Date.now(),
    name: btn.dataset.name,
    price: parseInt(btn.dataset.price),
    img: btn.dataset.img,
    category: btn.dataset.category
  };

  let wishlist = JSON.parse(localStorage.getItem("ahyera_wishlist") || "[]");
  const exists = wishlist.some(p => p.name === product.name);

  if (!exists) {
    wishlist.push(product);
    localStorage.setItem("ahyera_wishlist", JSON.stringify(wishlist));
    heart.classList.replace("far", "fas");
    heart.classList.add("heart-active");
    alert("Added to Wishlist!");
  } else {
    alert("Already in wishlist!");
  }
}
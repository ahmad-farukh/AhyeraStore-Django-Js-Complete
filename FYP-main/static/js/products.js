// Load products safely from Django script contexts
const productsDataEl = document.getElementById('products-data');
let allProducts = [];
try {
  allProducts = productsDataEl ? JSON.parse(productsDataEl.textContent || '[]') : [];
} catch (e) {
  allProducts = [];
}

// Global Wrapper function to push items into client storage context
window.addToWishlist = function(productId) {
  let wishlist = JSON.parse(localStorage.getItem("ahyera_wishlist") || "[]");
  
  // Loose typing (==) taake string/number id ka issue na aaye
  const product = allProducts.find(p => p.id == productId);
  if (!product) {
    alert("Product data synchronization failed!");
    return;
  }

  // Check if already in wishlist
  const exists = wishlist.some(item => item.id == product.id);
  if (exists) {
    alert(`${product.name} pehle se hi aap ki wishlist me maujood hai! ❤️`);
    return;
  }

  // Push minimal item payload mapping structure
  wishlist.push({
    id: product.id,
    name: product.name,
    price: product.price,
    img: product.image,
    category: product.category || 'Luxury'
  });

  localStorage.setItem("ahyera_wishlist", JSON.stringify(wishlist));
  
  // Pure dynamic browser toast alert notification
  alert(`Success: ${product.name} wishlist me add ho gaya! ❤️`);
};

// Map current product nodes to grid structure (Heart Button styled Dark Red)
function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  grid.innerHTML = products.map(p => `
    <div class="group bg-white rounded-2xl shadow-md overflow-hidden border hover:shadow-2xl transition-all duration-300 relative">
      <div class="overflow-hidden relative z-0">
        <img src="${p.image}" alt="${p.name}" class="w-full h-72 object-cover group-hover:scale-110 transition duration-500">
        
        <!-- Dark Red Floating Heart Target Node -->
        <button onclick="addToWishlist('${p.id}')" class="absolute top-4 right-4 z-20 bg-red-700 hover:bg-red-900 text-white w-10 h-10 rounded-full shadow-md flex items-center justify-center transition-colors duration-300 focus:outline-none">
          <i class="fas fa-heart text-lg"></i>
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
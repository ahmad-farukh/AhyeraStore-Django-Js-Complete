// Parse client storage stream array safe context setup
let wishlist = JSON.parse(localStorage.getItem("ahyera_wishlist") || "[]");

const wishlistItems = document.getElementById("wishlist-items");
const emptyState = document.getElementById("empty-state");
const wishlistContainer = document.getElementById("wishlist-container");
const totalPriceEl = document.getElementById("total-price");

// Bulletproof sync routine to run on update and deletion cycles
function updateWishlistCount() {
  const currentCount = wishlist.length;

  // Local Page Metric Blocks (Sidebar stats)
  const mainCountEl = document.getElementById("wishlist-count");
  if (mainCountEl) mainCountEl.textContent = currentCount;

  // Direct global layout selector target sync
  const navCountEl = document.getElementById("navbar-wishlist-count");
  if (navCountEl) navCountEl.textContent = currentCount;

  // Broad class query selector array synchronization
  document.querySelectorAll(".wishlist-count").forEach(el => {
    el.textContent = currentCount;
  });
}

function createWishlistItem(product) {
  const item = document.createElement("div");
  item.className = "border-b border-gray-100 last:border-0 p-8 hover:bg-gray-50 transition";
  item.innerHTML = `
    <div class="flex flex-col md:flex-row gap-8 items-center">
      <div class="w-32 h-32 rounded-2xl overflow-hidden shadow-lg flex-shrink-0">
        <img src="${product.img}" class="w-full h-full object-cover">
      </div>
      <div class="flex-1 text-center md:text-left">
        <h3 class="text-2xl font-bold text-gray-800 mb-2">${product.name}</h3>
        <p class="text-gray-600 text-lg">Category: <span class="font-medium capitalize">${product.category}</span></p>
      </div>
      <div class="text-3xl font-bold bg-gradient-to-r from-[#145efd] to-pink-600 bg-clip-text text-transparent">
        PKR ${product.price.toLocaleString()}
      </div>
      <div class="flex gap-4">
        <button onclick="moveToCart(${product.id})" class="bg-gradient-to-r from-[#145efd] to-pink-600 text-white px-8 py-4 rounded-xl font-bold hover:shadow-xl transition">
          Add to Cart
        </button>
        <button onclick="removeFromWishlist(${product.id})" class="text-red-600 hover:bg-red-50 p-4 rounded-xl transition">
          <i class="fas fa-trash text-xl"></i>
        </button>
      </div>
    </div>
  `;
  return item;
}

function renderWishlist() {
  updateWishlistCount();

  if (!wishlistItems) return; // Halt template injection if not on the dedicated page context

  if (wishlist.length === 0) {
    if (emptyState) emptyState.classList.remove("hidden");
    if (wishlistContainer) wishlistContainer.classList.add("hidden");
    return;
  }

  if (emptyState) emptyState.classList.add("hidden");
  if (wishlistContainer) wishlistContainer.classList.remove("hidden");
  wishlistItems.innerHTML = "";

  let total = 0;
  wishlist.forEach(p => {
    wishlistItems.appendChild(createWishlistItem(p));
    total += p.price;
  });

  if (totalPriceEl) totalPriceEl.textContent = total.toLocaleString();
}

window.removeFromWishlist = function(id) {
  wishlist = wishlist.filter(p => p.id !== id);
  localStorage.setItem("ahyera_wishlist", JSON.stringify(wishlist));
  renderWishlist();
  alert("Wishlist se item remove kar diya gaya!");
};

window.moveToCart = function(id) {
  const item = wishlist.find(p => p.id === id);
  if (item) {
    alert(`${item.name} cart me move ho gaya!`);
    removeFromWishlist(id);
  }
};

document.getElementById("move-all-btn")?.addEventListener("click", () => {
  if (wishlist.length > 0) {
    alert(`Tammam ${wishlist.length} items cart me shift ho gaye hain!`);
    wishlist = [];
    localStorage.setItem("ahyera_wishlist", JSON.stringify(wishlist));
    renderWishlist();
  }
});

// Run execution cycle safely upon template frame layout initialization
document.addEventListener("DOMContentLoaded", () => {
  renderWishlist();
});
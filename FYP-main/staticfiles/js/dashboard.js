// script.js
document.addEventListener("DOMContentLoaded", function () {

  const recentlyViewedEl = document.getElementById('recently-viewed-data');
  let recentlyViewed = [];
  try {
    recentlyViewed = recentlyViewedEl ? JSON.parse(recentlyViewedEl.textContent || '[]') : [];
  } catch (e) {
    recentlyViewed = [];
  }

  const container = document.getElementById("recently-viewed");
  if (!container) return;

  recentlyViewed.forEach(product => {
    container.innerHTML += `
      <div class="text-center group cursor-pointer">
        <div class="overflow-hidden rounded-2xl shadow-md group-hover:shadow-xl transition">
          <img src="${product.image}" class="w-full h-64 object-cover group-hover:scale-110 transition duration-500">
        </div>
        <h4 class="mt-4 font-bold text-lg">${product.name}</h4>
        <p class="text-pink-600 font-bold text-xl">PKR ${product.price.toLocaleString()}</p>
      </div>
    `;
  });

});
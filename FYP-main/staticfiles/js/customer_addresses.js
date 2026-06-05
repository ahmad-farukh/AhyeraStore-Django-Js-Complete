// addresses.js - Fully Working & Error-Free

let addresses = JSON.parse(localStorage.getItem("ahyera_addresses")) || [];

let editingId = null;
const container = document.getElementById("addresses-container");
const modal = document.getElementById("address-modal");
const form = document.getElementById("address-form");
const modalTitle = document.getElementById("modal-title");

// Render Addresses
function renderAddresses() {
  container.innerHTML = "";

  if (addresses.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-20">
        <i class="fas fa-map-marker-alt text-8xl text-gray-300 mb-6"></i>
        <h3 class="text-3xl font-bold text-gray-600">No addresses saved</h3>
        <p class="text-gray-500 mt-4">Add your first delivery address</p>
      </div>`;
    return;
  }

  addresses.forEach(addr => {
    const card = document.createElement("div");
    card.className = "bg-white rounded-2xl shadow-md border p-6 relative hover:shadow-lg transition";
    card.innerHTML = `
      <div class="absolute top-4 right-4 flex gap-3">
        <button onclick="editAddress(${addr.id})" class="text-blue-600 hover:bg-blue-50 p-2 rounded-lg">
          <i class="fas fa-edit"></i>
        </button>
        <button onclick="deleteAddress(${addr.id})" class="text-red-600 hover:bg-red-50 p-2 rounded-lg">
          <i class="fas fa-trash"></i>
        </button>
      </div>
      <div class="flex items-start gap-4">
        <i class="fas fa-${addr.isDefault ? 'home text-pink-600' : 'building text-gray-500'} text-3xl mt-1"></i>
        <div>
          <h3 class="font-bold text-lg">${addr.name}</h3>
          <p class="text-gray-600">${addr.address}</p>
          <p class="text-gray-600">${addr.city}, Pakistan</p>
          <p class="text-gray-700 font-medium mt-2">${addr.phone}</p>
          ${addr.isDefault ? '<span class="inline-block mt-3 px-4 py-2 bg-pink-100 text-pink-700 rounded-full text-sm font-bold">Default</span>' : ''}
          ${!addr.isDefault ? `<button onclick="setDefault(${addr.id})" class="mt-4 text-pink-600 hover:underline text-sm font-medium">Set as Default</button>` : ''}
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Open Add Modal
function openAddModal() {
  editingId = null;
  modalTitle.textContent = "Add New Address";
  form.reset();
  document.getElementById("city").value = "Karachi";
  document.getElementById("is-default").checked = false;
  modal.classList.remove("hidden");
}

// Edit Address
window.editAddress = function (id) {
  const addr = addresses.find(a => a.id === id);
  if (!addr) return;

  editingId = id;
  modalTitle.textContent = "Edit Address";
  document.getElementById("full-name").value = addr.name;
  document.getElementById("phone").value = addr.phone;
  document.getElementById("address").value = addr.address;
  document.getElementById("city").value = addr.city;
  document.getElementById("is-default").checked = addr.isDefault;
  modal.classList.remove("hidden");
};

// Close Modal
function closeModal() {
  modal.classList.add("hidden");
}

// Save (Add or Update)
form.onsubmit = function (e) {
  e.preventDefault();

  const newAddr = {
    id: editingId || Date.now(),
    name: document.getElementById("full-name").value.trim(),
    phone: document.getElementById("phone").value.trim(),
    address: document.getElementById("address").value.trim(),
    city: document.getElementById("city").value.trim(),
    isDefault: document.getElementById("is-default").checked
  };

  if (newAddr.isDefault) {
    addresses.forEach(a => a.isDefault = false);
  }

  if (editingId) {
    const index = addresses.findIndex(a => a.id === editingId);
    addresses[index] = newAddr;
  } else {
    addresses.push(newAddr);
  }

  localStorage.setItem("ahyera_addresses", JSON.stringify(addresses));
  closeModal();
  renderAddresses();
};

// Delete
window.deleteAddress = function (id) {
  if (confirm("Delete this address?")) {
    addresses = addresses.filter(a => a.id !== id);
    localStorage.setItem("ahyera_addresses", JSON.stringify(addresses));
    renderAddresses();
  }
};

// Set Default
window.setDefault = function (id) {
  addresses.forEach(a => a.isDefault = a.id === id);
  localStorage.setItem("ahyera_addresses", JSON.stringify(addresses));
  renderAddresses();
};

// Close modal on outside click
modal.addEventListener("click", function (e) {
  if (e.target === modal) closeModal();
});

// Start
renderAddresses();
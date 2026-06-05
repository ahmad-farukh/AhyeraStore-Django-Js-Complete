// script.js
document.addEventListener("DOMContentLoaded", function () {
  let order = JSON.parse(localStorage.getItem("current_order"));

  const successHeader = document.getElementById("success-header");
  const noOrderMsg = document.getElementById("no-order-message");

  const orderCard = document.getElementById("order-card");
  const orderItems = document.getElementById("order-items");
  const editItems = document.getElementById("edit-items");
  const editForm = document.getElementById("edit-form");

  // If no order or empty
  if (!order || !order.items || order.items.length === 0) {
    successHeader.classList.add("hidden");
    orderCard.classList.add("hidden");
    noOrderMsg.classList.remove("hidden");
    return;
  }

  // Set basic info
  document.getElementById("order-id").textContent = order.orderId || "#12345";
  document.getElementById("order-date").textContent = order.orderDate || new Date().toLocaleDateString();
  document.getElementById("payment-method").textContent = 
    order.paymentMethod === "cod" ? "Cash on Delivery" : order.paymentMethod.toUpperCase();

  // Ensure quantity exists
  order.items.forEach(item => {
    if (!item.quantity) item.quantity = 1;
  });

  // Render normal view
  function renderOrder() {
    orderItems.innerHTML = "";
    let total = 0;

    order.items.forEach(item => {
      const itemTotal = item.price * item.quantity;
      total += itemTotal;

      orderItems.innerHTML += `
        <div class="flex flex-col sm:flex-row justify-between items-center py-6 border-b">
          <div class="flex items-center gap-6 mb-4 sm:mb-0">
            <img src="${item.image}" class="w-28 h-28 object-cover rounded-xl shadow-lg">
            <div>
              <h3 class="text-xl font-bold">${item.name}</h3>
              <p class="text-gray-600">Size: <strong>${item.size || "Standard"}</strong> × ${item.quantity}</p>
            </div>
          </div>
          <p class="text-2xl font-bold text-pink-600">PKR ${itemTotal.toLocaleString()}</p>
        </div>`;
    });

    document.getElementById("total-amount").textContent = "PKR " + total.toLocaleString();
  }

  // Render edit mode
  function renderEditMode() {
    editItems.innerHTML = "";
    order.items.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "bg-white p-6 rounded-xl shadow";
      div.innerHTML = `
        <div class="flex justify-between items-center mb-4">
          <div class="flex items-center gap-4">
            <img src="${item.image}" class="w-20 h-20 rounded-lg">
            <h4 class="font-bold">${item.name}</h4>
          </div>
          <span class="text-xl font-bold text-pink-600">PKR <span class="price">${(item.price * item.quantity).toLocaleString()}</span></span>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <select class="size-select border rounded-xl px-4 py-3" data-index="${index}">
            ${["Small","Medium","Large","Custom"].map(s => 
              `<option ${item.size===s?"selected":""}>${s}</option>`
            ).join("")}
          </select>

          <div class="flex border rounded-xl">
            <button class="px-5 decrement" data-index="${index}">-</button>
            <input type="text" value="${item.quantity}" class="w-16 text-center font-bold qty" data-index="${index}">
            <button class="px-5 increment" data-index="${index}">+</button>
          </div>

          <button class="bg-red-600 text-white rounded-xl remove" data-index="${index}">Remove</button>
        </div>
      `;
      editItems.appendChild(div);
    });

    // Event Listeners
    document.querySelectorAll(".increment").forEach(btn => {
      btn.onclick = () => updateQty(parseInt(btn.dataset.index), 1);
    });
    document.querySelectorAll(".decrement").forEach(btn => {
      btn.onclick = () => updateQty(parseInt(btn.dataset.index), -1);
    });
    document.querySelectorAll(".remove").forEach(btn => {
      btn.onclick = () => {
        if(confirm("Remove this item?")) {
          order.items.splice(btn.dataset.index, 1);
          localStorage.setItem("current_order", JSON.stringify(order));
          renderEditMode();
          renderOrder();
        }
      };
    });
    document.querySelectorAll(".size-select").forEach(sel => {
      sel.onchange = () => {
        order.items[sel.dataset.index].size = sel.value;
      };
    });
  }

  function updateQty(index, change) {
    order.items[index].quantity = Math.max(1, order.items[index].quantity + change);
    document.querySelectorAll(".qty")[index].value = order.items[index].quantity;
    document.querySelectorAll(".price")[index].textContent = 
      (order.items[index].price * order.items[index].quantity).toLocaleString();
    renderOrder(); // Update total
  }

  // Buttons
  document.getElementById("edit-order-btn").onclick = () => {
    editForm.classList.toggle("hidden");
    if (!editForm.classList.contains("hidden")) renderEditMode();
  };

  document.getElementById("cancel-edit").onclick = () => {
    editForm.classList.add("hidden");
  };

  document.getElementById("save-changes").onclick = () => {
    localStorage.setItem("current_order", JSON.stringify(order));
    alert("Order updated successfully!");
    editForm.classList.add("hidden");
    renderOrder();
  };

  // Initial render
  renderOrder();
});
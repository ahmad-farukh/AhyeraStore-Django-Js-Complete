// Get data from server-provided JSON payloads
const dailyEl = document.getElementById('daily-sales-data');
const monthlyEl = document.getElementById('monthly-sales-data');
const topProductsEl = document.getElementById('top-products-data');

let dailyRows = [];
let monthlyRows = [];
let topProducts = [];

try {
  dailyRows = dailyEl ? JSON.parse(dailyEl.textContent || '[]') : [];
} catch (e) {
  dailyRows = [];
}

try {
  monthlyRows = monthlyEl ? JSON.parse(monthlyEl.textContent || '[]') : [];
} catch (e) {
  monthlyRows = [];
}

try {
  topProducts = topProductsEl ? JSON.parse(topProductsEl.textContent || '[]') : [];
} catch (e) {
  topProducts = [];
}

const dailyData = {
  labels: dailyRows.map((r) => (r.date ? String(r.date) : '')),
  values: dailyRows.map((r) => Number(r.total_sales || 0)),
};

const monthlyData = {
  labels: monthlyRows.map((r) => (r.month ? String(r.month).slice(0, 7) : '')),
  values: monthlyRows.map((r) => Number(r.total_sales || 0)),
};

// Daily Chart
new Chart(document.getElementById('dailyChart'), {
  type: 'line',
  data: {
    labels: dailyData.labels,
    datasets: [{
      label: 'Daily Sales (₨)',
      data: dailyData.values,
      borderColor: '#1e40af',
      backgroundColor: 'rgba(30, 64, 175, 0.1)',
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#1e40af',
      pointRadius: 5
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } }
  }
});

// Monthly Chart
new Chart(document.getElementById('monthlyChart'), {
  type: 'bar',
  data: {
    labels: monthlyData.labels,
    datasets: [{
      label: 'Monthly Revenue (₨)',
      data: monthlyData.values,
      backgroundColor: '#1e40af',
      borderRadius: 8
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } }
  }
});

// Top Products
const topDiv = document.getElementById('topProducts');
if (topDiv) {
  topDiv.innerHTML = '';
  topProducts.forEach((p, i) => {
    const div = document.createElement('div');
    div.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg border';
    const productName = p.product__name || p.name || '';
    const sold = Number(p.quantity_sold || p.sold || 0);
    const revenue = Number(p.revenue || 0);
    div.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-2xl font-bold text-blue-900">${i + 1}</span>
        <div>
          <p class="font-bold text-gray-800">${productName}</p>
          <p class="text-xs text-gray-600">${sold} units sold</p>
        </div>
      </div>
      <p class="font-bold text-blue-900">₨${revenue.toLocaleString()}</p>
    `;
    topDiv.appendChild(div);
  });
}
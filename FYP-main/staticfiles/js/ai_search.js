// Predictive Search Suggestions
const suggestionsEl = document.getElementById('ai-suggestions-data');
let suggestions = [];
try {
  suggestions = suggestionsEl ? JSON.parse(suggestionsEl.textContent || '[]') : [];
} catch (e) {
  suggestions = [];
}

const visualCountEl = document.getElementById('ai-visual-result-count');
let visualResultCount = 0;
try {
  visualResultCount = visualCountEl ? Number(JSON.parse(visualCountEl.textContent || '0')) : 0;
} catch (e) {
  visualResultCount = 0;
}

const textInput = document.getElementById('text-search');
const suggestionBox = document.getElementById('suggestions');
const suggestionList = document.getElementById('suggestion-list');

if (!textInput || !suggestionBox || !suggestionList) {
  // Page does not include the AI search UI
} else {

  textInput.addEventListener('input', function () {
    const query = this.value.toLowerCase().trim();

    if (query.length < 2) {
      suggestionBox.classList.add('hidden');
      return;
    }

    const filtered = suggestions.filter(item => item.toLowerCase().includes(query));

    if (filtered.length === 0) {
      suggestionList.innerHTML = `<div class="px-6 py-3 text-gray-500">No suggestions found</div>`;
    } else {
      suggestionList.innerHTML = filtered.map(item => `
        <div class="search-suggestion px-6 py-3 flex items-center justify-between cursor-pointer" onclick="selectSuggestion('${item}')">
          <span class="flex items-center gap-3">
            <i class="fas fa-search text-pink-500"></i>
            ${item}
          </span>
          <i class="fas fa-arrow-up-right-from-square text-gray-400"></i>
        </div>
      `).join('');
    }

    suggestionBox.classList.remove('hidden');
  });

  // Select suggestion
  window.selectSuggestion = function(text) {
    textInput.value = text;
    suggestionBox.classList.add('hidden');
    showDidYouMean(text);
  }

  // Click outside → hide suggestions
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#search-container')) {
      suggestionBox.classList.add('hidden');
    }
  });

  // Image Upload Preview
  window.handleFileSelect = function(e) {
    const file = e.target.files[0];
    if (file) showImagePreview(file);
  }

  window.previewAndSubmit = function(e) {
    handleFileSelect(e);
    const form = document.getElementById('image-search-form');
    if (form) {
      form.submit();
    }
  }

  window.handleDrop = function(e) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const input = document.getElementById('image-upload');
      if (input) {
        // Create a new FileList with the dropped file
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
      }
      showImagePreview(file);
    }
    document.getElementById('drop-zone').classList.remove('bg-pink-50', 'border-pink-500');
  }

  function showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const previewImg = document.getElementById('preview-img');
      const uploadedPreview = document.getElementById('uploaded-preview');
      const dropZone = document.getElementById('drop-zone');
      
      if (previewImg) previewImg.src = e.target.result;
      if (uploadedPreview) uploadedPreview.classList.remove('hidden');
      if (dropZone) dropZone.classList.add('border-pink-500', 'bg-pink-50');
      
      // ✅ REMOVED: Fake alert simulation
      // The form will handle actual submission and results
    };
    reader.readAsDataURL(file);
  }

  // Did you mean suggestions
  function showDidYouMean(query) {
    const container = document.getElementById('did-you-mean');
    if (container) {
      container.classList.remove('hidden');
    }
  }
}
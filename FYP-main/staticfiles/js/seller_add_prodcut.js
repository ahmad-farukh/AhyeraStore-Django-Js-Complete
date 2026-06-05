let cropper = null;
let croppedImages = [];

// Select Elements
const imageInput = document.getElementById("imageInput");
const uploadArea = document.getElementById("uploadArea");
const imageThumbnails = document.getElementById("imageThumbnails");
const cropModal = document.getElementById("cropModal");
const imageToCrop = document.getElementById("imageToCrop");

// Click to open file
uploadArea.addEventListener("click", () => imageInput.click());

// When image selected
imageInput.addEventListener("change", function (e) {
    if (!e.target.files[0]) return;

    const file = e.target.files[0];

    // Fix for large images – compress first
    const reader = new FileReader();
    reader.onload = function (ev) {
        compressImage(ev.target.result, 2000, (compressedData) => {
            imageToCrop.src = compressedData;
            cropModal.classList.remove("hidden");

            setTimeout(() => {
                if (cropper) cropper.destroy();
                cropper = new Cropper(imageToCrop, {
                    aspectRatio: 1,
                    viewMode: 2,
                    autoCropArea: 1,
                });
            }, 150);
        });
    };
    reader.readAsDataURL(file);
});

// Cancel crop
function cancelCrop() {
    cropModal.classList.add("hidden");
    if (cropper) cropper.destroy();
    cropper = null;
}

// Save cropped image
function saveCroppedImage() {
    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas({
        width: 1000,
        height: 1000,
        fillColor: "#fff",
    });

    canvas.toBlob(
        (blob) => {
            const url = URL.createObjectURL(blob);
            croppedImages.push(url);
            renderThumbnails();
            updatePreviewImage();
            cancelCrop();
        },
        "image/jpeg",
        0.9
    );
}

// Render thumbnails
function renderThumbnails() {
    imageThumbnails.innerHTML = "";
    croppedImages.forEach((url, index) => {
        imageThumbnails.innerHTML += `
            <div class="relative group">
                <img src="${url}" class="w-28 h-28 object-cover rounded-xl" />
                <button onclick="removeImage(${index})"
                class="absolute -top-2 -right-2 bg-red-600 text-white w-8 h-8 rounded-full opacity-0 group-hover:opacity-100">×</button>
            </div>
        `;
    });
}

// Remove image
function removeImage(i) {
    croppedImages.splice(i, 1);
    renderThumbnails();
    updatePreviewImage();
}

// Update main image
function updatePreviewImage() {
    const container = document.getElementById("previewImageContainer");
    if (croppedImages.length > 0) {
        container.innerHTML = `<img src="${croppedImages[0]}" class="w-full h-80 object-cover" />`;
    } else {
        container.innerHTML = `<p class="text-gray-400">No image selected</p>`;
    }
}

// Large images ko auto compress krny wala function
function compressImage(src, maxSize, callback) {
    const img = new Image();
    img.src = src;

    img.onload = () => {
        const canvas = document.createElement("canvas");
        let width = img.width;
        let height = img.height;

        if (width > maxSize || height > maxSize) {
            if (width > height) {
                height *= maxSize / width;
                width = maxSize;
            } else {
                width *= maxSize / height;
                height = maxSize;
            }
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        callback(canvas.toDataURL("image/jpeg", 0.9));
    };
}

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const removeImgBtn = document.getElementById('remove-img-btn');
    const predictBtn = document.getElementById('predict-btn');
    const scannerLine = document.getElementById('scanner-line');
    
    const uploadSection = document.getElementById('upload-section');
    const resultSection = document.getElementById('result-section');
    
    const resultImage = document.getElementById('result-image');
    const resultClass = document.getElementById('result-class');
    const resultConfidenceText = document.getElementById('result-confidence-text');
    const progressBarFill = document.getElementById('progress-bar-fill');

    const resultSuccess = document.getElementById('result-success');
    const resultError = document.getElementById('result-error');
    const errorConfidenceText = document.getElementById('error-confidence-text');
    
    const resetBtn = document.getElementById('reset-btn');
    const homeBtn = document.getElementById('home-btn');

    let currentFile = null;

    // --- Drag & Drop Handlers ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                currentFile = file;
                showPreview(file);
            } else {
                alert('Harap unggah file gambar.');
            }
        }
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            imagePreview.src = reader.result;
            dropZone.style.display = 'none';
            previewArea.style.display = 'flex';
        }
    }

    removeImgBtn.addEventListener('click', () => {
        resetUploadState();
    });

    function resetUploadState() {
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '#';
        previewArea.style.display = 'none';
        dropZone.style.display = 'flex';
        scannerLine.classList.remove('active');
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<iconify-icon icon="ph:magic-wand"></iconify-icon> Identifikasi Ras';
    }

    // --- Prediction Handler ---
    predictBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI State -> Loading (Scanning Animation)
        scannerLine.classList.add('active');
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<iconify-icon icon="line-md:loading-twotone-loop"></iconify-icon> Menganalisis...';

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Success UI Swap
                setTimeout(() => {
                    uploadSection.style.display = 'none';
                    resultSection.style.display = 'flex';
                    resultImage.src = imagePreview.src;

                    const confValue = parseFloat(data.confidence);

                    if (data.is_dog === false) {
                        // NOT A DOG — show error panel
                        resultSuccess.style.display = 'none';
                        resultError.style.display = 'flex';
                        errorConfidenceText.textContent = `${confValue.toFixed(1)}%`;
                    } else {
                        // VALID DOG — show normal result
                        resultError.style.display = 'none';
                        resultSuccess.style.display = 'block';
                        resultClass.textContent = data.class;
                        resultConfidenceText.textContent = `${confValue.toFixed(1)}%`;
                        
                        // Animate Progress Bar
                        setTimeout(() => {
                            progressBarFill.style.width = `${confValue}%`;
                        }, 100);
                    }

                }, 800); // Artificial delay to let user see scanning animation

            } else {
                throw new Error(data.error || 'Terjadi kesalahan pada server.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Prediksi Gagal: ' + error.message);
            // Revert state
            resetUploadState();
        }
    });

    // --- Common Reset Logic ---
    function goBackToUpload() {
        resultSection.style.display = 'none';
        uploadSection.style.display = 'flex';
        progressBarFill.style.width = '0%';
        // Reset both panels
        resultSuccess.style.display = 'block';
        resultError.style.display = 'none';
    }

    // --- Coba Lagi Handler ---
    resetBtn.addEventListener('click', () => {
        goBackToUpload();
        resetUploadState();
    });
    
    // --- Beranda Handler ---
    homeBtn.addEventListener('click', () => {
        goBackToUpload();
        resetUploadState();
    });

    // --- Fakta Menarik ---
    const funFacts = [
        "Indra penciuman anjing 10.000 hingga 100.000 kali lebih sensitif daripada manusia!",
        "Chihuahua lahir dengan titik lunak di tengkorak mereka, sama seperti bayi manusia.",
        "Basenji adalah satu-satunya ras anjing yang tidak bisa menggonggong, tapi mereka bisa yodel!",
        "Sidik hidung anjing itu unik, mirip seperti sidik jari manusia.",
        "Greyhound bisa mencapai kecepatan hingga 72 km per jam.",
        "Saat anjing menendang tanah setelah buang air, mereka menggunakan kelenjar aroma di kaki untuk menandai wilayah.",
        "Anak anjing lahir dalam keadaan buta, tuli, dan tidak bergigi.",
        "Afghan Hound dianggap sebagai salah satu ras anjing tertua yang masih ada.",
        "Dalmatian lahir sepenuhnya putih; bintik-bintik mereka berkembang seiring pertumbuhan.",
        "Suhu tubuh normal anjing adalah antara 38,3 dan 39,2 derajat Celcius."
    ];

    const factElement = document.getElementById('fun-fact');
    
    if (factElement) {
        // Change fact every 10 seconds
        setInterval(() => {
            const randomIndex = Math.floor(Math.random() * funFacts.length);
            // Fade out
            factElement.style.opacity = '0';
            setTimeout(() => {
                factElement.textContent = funFacts[randomIndex];
                // Fade in
                factElement.style.transition = 'opacity 0.5s';
                factElement.style.opacity = '1';
            }, 500); // Wait for fade out
        }, 10000);

        // Set initial random fact
        factElement.textContent = funFacts[Math.floor(Math.random() * funFacts.length)];
    }
});

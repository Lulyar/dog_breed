document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const removeImgBtn = document.getElementById('remove-img-btn');
    const predictBtn = document.getElementById('predict-btn');
    const scannerLine = document.getElementById('scanner-line'); // New
    
    const uploadSection = document.getElementById('upload-section');
    const resultSection = document.getElementById('result-section');
    
    const resultImage = document.getElementById('result-image');
    const resultClass = document.getElementById('result-class');
    const resultConfidenceText = document.getElementById('result-confidence-text'); // New
    const progressBarFill = document.getElementById('progress-bar-fill'); // New
    
    const resetBtn = document.getElementById('reset-btn');
    const homeBtn = document.getElementById('home-btn'); // New

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
                alert('Please upload an image file.');
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
        predictBtn.innerHTML = '<iconify-icon icon="ph:magic-wand"></iconify-icon> Identify Breed';
    }

    // --- Prediction Handler ---
    predictBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI State -> Loading (Scanning Animation)
        scannerLine.classList.add('active');
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<iconify-icon icon="line-md:loading-twotone-loop"></iconify-icon> Analyzing...';

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
                    
                    resultImage.src = imagePreview.src; // Reuse preview image
                    resultClass.textContent = data.class;
                    
                    // Parse confidence (e.g., "98.50%")
                    const confValue = parseFloat(data.confidence);
                    resultConfidenceText.textContent = `${confValue.toFixed(1)}%`;
                    
                    // Animate Progress Bar
                    setTimeout(() => {
                        progressBarFill.style.width = `${confValue}%`;
                    }, 100);

                }, 800); // Artificial delay to let user see scanning animation

            } else {
                throw new Error(data.error || 'Server error occurred.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Prediction Failed: ' + error.message);
            // Revert state
            resetUploadState();
        }
    });

    // --- Common Reset Logic ---
    function goBackToUpload() {
        resultSection.style.display = 'none';
        uploadSection.style.display = 'flex';
        progressBarFill.style.width = '0%';
    }

    // --- Try Another Handler ---
    resetBtn.addEventListener('click', () => {
        goBackToUpload();
        resetUploadState();
    });
    
    // --- Home Handler ---
    homeBtn.addEventListener('click', () => {
        goBackToUpload();
        resetUploadState(); // Essentially the same logic but a different button visually
    });
    // --- Fun Facts Logic ---
    const funFacts = [
        "A dog’s sense of smell is 10,000 to 100,000 times more sensitive than a human’s!",
        "Chihuahuas are born with a soft spot in their skull, just like human babies.",
        "The Basenji is the only breed of dog that can't bark, but they can yodel!",
        "A dog's nose print is unique, much like a person's fingerprint.",
        "Greyhounds can reach speeds up to 45 miles per hour.",
        "When dogs kick after going to the bathroom, they are using the scent glands on their paws to mark their territory.",
        "Puppies are born blind, deaf, and toothless.",
        "The Afghan Hound is considered one of the oldest dog breeds in existence.",
        "Dalmatians are born completely white; their spots develop as they grow older.",
        "A dog's normal body temperature is between 101 and 102.5 degrees Fahrenheit."
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

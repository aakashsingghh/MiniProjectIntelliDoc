/**
 * INTELLIDOC - Main frontend JS logic
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark mode logic
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlEl = document.documentElement;

    // Load from local storage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlEl.setAttribute('data-bs-theme', savedTheme);
        updateIcon(savedTheme);
    }

    if(themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlEl.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            htmlEl.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });
    }

    function updateIcon(theme) {
        if(theme === 'dark') {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        } else {
            themeIcon.classList.remove('bi-sun-fill');
            themeIcon.classList.add('bi-moon-fill');
        }
    }

    // 2. Drag & Drop Upload Handlers
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileNameText = document.getElementById('fileNameText');
    const uploadForm = document.getElementById('uploadForm');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (dropZone && fileInput) {
        // Prevent default browser behavior on drops
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Add visual cues when dragging hovering
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        // Handle the drop natively
        dropZone.addEventListener('drop', handleDrop, false);
        
        // Handle select file button click or standard file input change
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files; // Assign files to the actual input
            handleFiles(files);
        }
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Display filename securely and nicely
            fileNameText.textContent = file.name;
            fileNameDisplay.classList.remove('d-none');
            fileNameDisplay.classList.add('d-flex');
            
            // Add a little bounce animation to notify success
            fileNameDisplay.style.animation = 'none';
            fileNameDisplay.offsetHeight; // trigger reflow
            fileNameDisplay.style.animation = 'pulse 0.5s';
        }
    }

    // 3. Setup loading overlay on form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            if (fileInput.files.length > 0) {
                // Show the cool spinner overlay
                loadingOverlay.classList.remove('d-none');
                loadingOverlay.classList.add('d-flex');
                
                // Disable button so we don't submit twice
                const btn = document.getElementById('submitBtn');
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            }
        });
    }
});

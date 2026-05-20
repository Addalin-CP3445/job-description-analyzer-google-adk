document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const submitBtn = document.getElementById('submit-btn');
    const resultsSection = document.getElementById('results-section');
    const formSection = document.querySelector('.form-section');
    const reportContent = document.getElementById('report-content');
    const resetBtn = document.getElementById('reset-btn');
    
    // File upload logic
    const fileInput = document.querySelector('.file-input');
    const fileDropArea = document.getElementById('drop-area');
    const fileMsg = document.querySelector('.file-msg');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileMsg.textContent = e.target.files[0].name;
            fileDropArea.style.borderColor = 'var(--accent)';
        } else {
            fileMsg.textContent = 'Choose a file or drag it here';
            fileDropArea.style.borderColor = 'var(--glass-border)';
        }
    });

    fileInput.addEventListener('dragenter', () => {
        fileDropArea.classList.add('dragover');
    });

    fileInput.addEventListener('dragleave', () => {
        fileDropArea.classList.remove('dragover');
    });

    fileInput.addEventListener('drop', () => {
        fileDropArea.classList.remove('dragover');
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        const jdText = document.getElementById('jd-text').value;

        if (!file || !jdText) {
            alert('Please provide both a CV file and a Job Description.');
            return;
        }

        // Setup UI for loading
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append('cv_file', file);
        formData.append('jd_text', jdText);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Analysis failed');
            }

            // Parse Markdown to HTML
            reportContent.innerHTML = marked.parse(data.report);

            // Switch views
            formSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');

        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    // Reset Form
    resetBtn.addEventListener('click', () => {
        form.reset();
        fileMsg.textContent = 'Choose a file or drag it here';
        fileDropArea.style.borderColor = 'var(--glass-border)';
        resultsSection.classList.add('hidden');
        formSection.classList.remove('hidden');
    });
});

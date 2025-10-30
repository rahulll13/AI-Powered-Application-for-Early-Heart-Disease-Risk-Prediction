
let activeInput = null;
let historyChart = null; 

// --- Helper function to handle different API errors ---
function handleApiError(errorDiv, data, response) {
    if (response.status === 401 || response.status === 422) {
        // Handle token-related errors (Unauthorized, Expired)
        errorDiv.innerHTML = `<div class="alert alert-danger mt-4">Your session has expired. Redirecting to login...</div>`;
        // Redirect to login after 3 seconds
        setTimeout(() => {
            localStorage.removeItem('accessToken');
            window.location.href = 'index.html';
        }, 3000);
    } else {
        // Handle other server errors (e.g., 500 Internal Server Error)
        const message = data.message || 'A server error occurred. Please try again later.';
        errorDiv.innerHTML = `<div class="alert alert-danger mt-4">${message}</div>`;
    }
}

// Fetches and displays the user's prediction history and renders the chart
async function loadPredictionHistory() {
    const historyContainer = document.getElementById('history-container');
    if (!historyContainer) return;

    try {
        const response = await fetch(`${API_URL}/predictions`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();

        if (!response.ok) {
            handleApiError(historyContainer, data, response);
            return;
        }

        const history = data;
        
        const ctx = document.getElementById('historyChart');
        if (ctx) {
            if (historyChart) {
                historyChart.destroy(); // Destroy old chart before drawing new one
            }
            if (history.length > 0) {
                const riskCounts = { 'Low': 0, 'Medium': 0, 'High': 0 };
                history.forEach(pred => {
                    if (pred.risk_category in riskCounts) {
                        riskCounts[pred.risk_category]++;
                    }
                });

                historyChart = new Chart(ctx.getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                        datasets: [{
                            label: 'Prediction Distribution',
                            data: [riskCounts.Low, riskCounts.Medium, riskCounts.High],
                            backgroundColor: ['rgb(25, 135, 84)', 'rgb(255, 193, 7)', 'rgb(220, 53, 69)'],
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: true, text: 'Prediction Risk Distribution' }
                        }
                    }
                });
            }
        }

        if (history.length === 0) {
            historyContainer.innerHTML = '<p>You have no past predictions.</p>';
            return;
        }

        let historyHtml = '<ul class="list-group">';
        history.forEach(pred => {
            const date = new Date(pred.timestamp + 'Z').toLocaleString();
            let badgeClass = 'bg-success';
            if (pred.risk_category === 'Medium') badgeClass = 'bg-warning text-dark';
            if (pred.risk_category === 'High') badgeClass = 'bg-danger';
            historyHtml += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        Prediction made on <strong>${date}</strong>
                        <span class="badge ${badgeClass} rounded-pill ms-2">${pred.risk_category} Risk</span>
                    </div>
                    <button class="btn btn-outline-secondary btn-sm download-pdf-btn" data-id="${pred.id}">
                        Download PDF
                    </button>
                </li>`;
        });
        historyHtml += '</ul>';
        historyContainer.innerHTML = historyHtml;

    } catch (error) {
        console.error('Network error loading prediction history:', error);
        historyContainer.innerHTML = '<p class="text-danger">A network error occurred. Please ensure the server is running.</p>';
    }
}

// Finds all numbers in a block of text and wraps them in a clickable span
function processOcrText(text) {
    if (!text) return 'No text found.';
    const regex = /(\d+\.?\d*)/g;
    return text.replace(regex, '<span class="clickable-ocr-number">$1</span>');
}

// Loads the navbar from a separate file
async function loadNavbar() {
    try {
        const response = await fetch('_navbar.html');
        if (!response.ok) return;
        const navbarHtml = await response.text();
        document.getElementById('navbar-container').innerHTML = navbarHtml;
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('accessToken');
                window.location.href = 'index.html';
            });
        }
    } catch (error) {
        console.error('Failed to load the navbar:', error);
    }
}


// --- Main script execution after the page is loaded ---
document.addEventListener('DOMContentLoaded', () => {
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    loadNavbar();
    loadPredictionHistory();

    const predictionForm = document.getElementById('predictionForm');
    const uploadForm = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('resultDiv');
    const uploadResultDiv = document.getElementById('uploadResultDiv');
    const historyContainer = document.getElementById('history-container');

    if (predictionForm) {
        predictionForm.addEventListener('focusin', (e) => {
            if (e.target.tagName === 'INPUT') activeInput = e.target;
        });

        predictionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            resultDiv.innerHTML = '<div class="alert alert-info">Getting prediction...</div>';
            
            const formData = {
                age: parseInt(document.getElementById('age').value), sex: parseInt(document.getElementById('sex').value),
                cp: parseInt(document.getElementById('cp').value), trestbps: parseInt(document.getElementById('trestbps').value),
                chol: parseInt(document.getElementById('chol').value), fbs: parseInt(document.getElementById('fbs').value),
                restecg: parseInt(document.getElementById('restecg').value), thalach: parseInt(document.getElementById('thalach').value),
                exang: parseInt(document.getElementById('exang').value), oldpeak: parseFloat(document.getElementById('oldpeak').value),
                slope: parseInt(document.getElementById('slope').value), ca: parseInt(document.getElementById('ca').value),
                thal: parseInt(document.getElementById('thal').value),
            };

            try {
                const response = await fetch(`${API_URL}/predict`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();

                if (response.ok) {
                    let resultClass = 'alert-success';
                    if (data.risk_category === 'Medium') resultClass = 'alert-warning text-dark';
                    if (data.risk_category === 'High') resultClass = 'alert-danger';
                    resultDiv.innerHTML = `<div class="alert ${resultClass} mt-4"><h4>Prediction Result</h4><p><strong>Risk Category:</strong> ${data.risk_category}</p><p><strong>Probability of Heart Disease:</strong> ${(data.probability * 100).toFixed(2)}%</p></div>`;
                    loadPredictionHistory();
                } else {
                    handleApiError(resultDiv, data, response);
                }
            } catch (error) {
                console.error('Network error during prediction:', error);
                resultDiv.innerHTML = `<div class="alert alert-danger mt-4">A network error occurred. Please try again.</div>`;
            }
        });
    }

    if (uploadForm) {
        const fileInput = document.getElementById('documentFile');
        const uploadButton = document.getElementById('uploadButton');
        const dropZonePrompt = uploadForm.querySelector(".drop-zone__prompt");
        uploadForm.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length) updateDropZonePrompt(fileInput.files[0]);
        });
        ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => uploadForm.addEventListener(eventName, preventDefaults, false));
        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
        ["dragenter", "dragover"].forEach(eventName => uploadForm.addEventListener(eventName, () => uploadForm.classList.add("drop-zone--over"), false));
        ["dragleave", "drop"].forEach(eventName => uploadForm.addEventListener(eventName, () => uploadForm.classList.remove("drop-zone--over"), false));
        uploadForm.addEventListener("drop", (e) => {
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateDropZonePrompt(fileInput.files[0]);
            }
        });
        function updateDropZonePrompt(file) { dropZonePrompt.innerHTML = `<strong>Selected file:</strong> ${file.name}`; }
        
        uploadButton.addEventListener('click', async () => {
            uploadResultDiv.innerHTML = '<div class="alert alert-info">Uploading...</div>';
            if (fileInput.files.length === 0) {
                uploadResultDiv.innerHTML = '<div class="alert alert-danger">Please select a file to upload.</div>'; return;
            }
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('document', file);
            try {
                const response = await fetch(`${API_URL}/upload-document`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    const highlightedText = processOcrText(data.extracted_text);
                    uploadResultDiv.innerHTML = `<div class="alert alert-success mt-4"><h4>Upload Successful!</h4><p><strong>Filename:</strong> ${data.filename}</p><p><strong>Extracted Text (click a number to fill the form):</strong></p><pre class="bg-white p-2 rounded">${highlightedText}</pre></div>`;
                } else {
                    handleApiError(uploadResultDiv, data, response);
                }
            } catch (error) {
                 console.error('Network error during upload:', error);
                 uploadResultDiv.innerHTML = `<div class="alert alert-danger mt-4">A network error occurred. Please try again.</div>`;
            }
        });
    }

    if (uploadResultDiv) {
        uploadResultDiv.addEventListener('click', (e) => {
            if (e.target.classList.contains('clickable-ocr-number') && activeInput) {
                activeInput.value = e.target.textContent;
                const formInputs = Array.from(predictionForm.querySelectorAll('input'));
                const currentIndex = formInputs.indexOf(activeInput);
                if (currentIndex !== -1 && currentIndex < formInputs.length - 1) {
                    const nextInput = formInputs[currentIndex + 1];
                    nextInput.focus();
                }
            }
        });
    }
    
    if (historyContainer) {
        historyContainer.addEventListener('click', async (e) => {
            if (e.target.classList.contains('download-pdf-btn')) {
                const predictionId = e.target.dataset.id;
                e.target.textContent = 'Downloading...';
                e.target.disabled = true;
                try {
                    const response = await fetch(`${API_URL}/predictions/${predictionId}/export`, {
                        method: 'GET',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!response.ok) throw new Error('Download failed');
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `prediction_report_${predictionId}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                } catch (error) {
                    console.error('PDF Download error:', error);
                    alert('Failed to download PDF report.');
                } finally {
                    e.target.textContent = 'Download PDF';
                    e.target.disabled = false;
                }
            }
        });
    }
});


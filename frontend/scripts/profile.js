// frontend/scripts/profile.js
// NOTE: API_URL and token are now defined in main.js

let profileChart = null;

async function loadProfileData() {
    const profileUsername = document.getElementById('profileUsername');
    const profileEmail = document.getElementById('profileEmail');
    const profilePredictionCount = document.getElementById('profilePredictionCount');
    const profileStreak = document.getElementById('profileStreak');

    try {
        const response = await fetch(`${API_URL}/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch profile data');

        const data = await response.json();
        if(profileUsername) profileUsername.textContent = data.username;
        if(profileEmail) profileEmail.textContent = data.email;
        if(profilePredictionCount) profilePredictionCount.textContent = `Total Predictions Made: ${data.prediction_count}`;
        if(profileStreak) profileStreak.textContent = `Current Streak: ${data.prediction_streak}`; // Populate streak
        // Also load the prediction history for this page
        loadPredictionHistory();
    } catch (error) {
        console.error("Error loading profile:", error);
        if(profileUsername) profileUsername.textContent = 'Could not load profile data.';
    }
}

async function loadPredictionHistory() {
    const historyContainer = document.getElementById('history-container');
    if (!historyContainer) return;

    try {
        const response = await fetch(`${API_URL}/predictions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Could not load history');
        
        const history = await response.json();
        
        const ctx = document.getElementById('profileChart');
        if (ctx) {
            if (profileChart) {
                profileChart.destroy();
            }
            if (history.length > 0) {
                const riskCounts = { 'Low': 0, 'Medium': 0, 'High': 0 };
                history.forEach(pred => {
                    if (pred.risk_category in riskCounts) riskCounts[pred.risk_category]++;
                });

                profileChart = new Chart(ctx.getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                        datasets: [{
                            data: [riskCounts.Low, riskCounts.Medium, riskCounts.High],
                            backgroundColor: ['rgb(25, 135, 84)', 'rgb(255, 193, 7)', 'rgb(220, 53, 69)'],
                        }]
                    },
                    options: { responsive: true, plugins: { title: { display: true, text: 'Prediction Risk Distribution' } } }
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
                    <div>Prediction on <strong>${date}</strong> <span class="badge ${badgeClass} rounded-pill ms-2">${pred.risk_category} Risk</span></div>
                    <button class="btn btn-outline-secondary btn-sm download-pdf-btn" data-id="${pred.id}">Download PDF</button>
                </li>`;
        });
        historyHtml += '</ul>';
        historyContainer.innerHTML = historyHtml;

    } catch (error) {
        console.error('Failed to load prediction history:', error);
        historyContainer.innerHTML = '<p class="text-danger">Could not load prediction history.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadProfileData();

    const historyContainer = document.getElementById('history-container');
    if (historyContainer) {
        historyContainer.addEventListener('click', async (e) => {
            if (e.target.classList.contains('download-pdf-btn')) {
                const predictionId = e.target.dataset.id;
                e.target.textContent = 'Downloading...';
                e.target.disabled = true;
                try {
                    const response = await fetch(`${API_URL}/predictions/${predictionId}/export`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!response.ok) throw new Error('Download failed');
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `prediction_report_${predictionId}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
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
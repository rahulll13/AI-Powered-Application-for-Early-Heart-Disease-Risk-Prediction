// frontend/scripts/doctor-dashboard.js

// NOTE: The global variables 'API_URL' and 'token' are defined in main.js

async function loadPatientList() {
    const container = document.getElementById('patient-list-container');
    
    // Ensure the token is available before making the request
    if (!container || !token) {
        if (!token) {
             window.location.href = 'index.html'; // Redirect if not logged in
        }
        return;
    }

    try {
        const response = await fetch(`${API_URL}/doctor/patients`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();

        if (!response.ok) {
            // If the user is not a doctor, the backend sends a 403 error.
            const errorMessage = data.message || 'You do not have permission to view this page.';
            container.innerHTML = `<div class="alert alert-danger m-0">${errorMessage}</div>`;
            return;
        }

        if (data.length === 0) {
            container.innerHTML = '<div class="alert alert-info m-0">There are no patient accounts in the system yet.</div>';
            return;
        }

        // Build the HTML for the patient table
        let tableHtml = `
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Total Predictions</th>
                        <th class="text-end">Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;
        data.forEach(patient => {
            tableHtml += `
                <tr>
                    <td>${patient.username}</td>
                    <td>${patient.email}</td>
                    <td>${patient.prediction_count}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-danger remove-patient-btn" data-id="${patient.id}" data-username="${patient.username}">Remove</button>
                    </td>
                </tr>
            `;
        });
        tableHtml += '</tbody></table>';
        container.innerHTML = tableHtml;

    } catch (error) {
        console.error('Failed to load patient list:', error);
        container.innerHTML = '<div class="alert alert-danger m-0">A network error occurred while trying to load patient data.</div>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadPatientList();

    const container = document.getElementById('patient-list-container');
    if (container) {
        container.addEventListener('click', async (e) => {
            // Check if a remove button was clicked
            if (e.target.classList.contains('remove-patient-btn')) {
                const patientId = e.target.dataset.id;
                const patientUsername = e.target.dataset.username;

                // Ask for confirmation
                if (confirm(`Are you sure you want to remove the patient '${patientUsername}'? This action is permanent.`)) {
                    try {
                        const response = await fetch(`${API_URL}/doctor/patients/${patientId}`, {
                            method: 'DELETE',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });

                        if (!response.ok) {
                            const errorData = await response.json();
                            throw new Error(errorData.message || 'Failed to remove patient.');
                        }
                        
                        // If successful, just reload the list
                        loadPatientList();

                    } catch (error) {
                        console.error('Failed to remove patient:', error);
                        alert(`Error: ${error.message}`);
                    }
                }
            }
        });
    }
});
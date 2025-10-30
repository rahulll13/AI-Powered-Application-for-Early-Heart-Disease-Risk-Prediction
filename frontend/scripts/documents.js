// frontend/scripts/documents.js
// NOTE: API_URL and token are now defined in main.js and are available globally.

// Function to fetch and display the list of documents
async function loadDocuments() {
    const documentsContainer = document.getElementById('documents-container');
    if (!documentsContainer) return;

    try {
        const response = await fetch(`${API_URL}/documents`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch documents');

        const documents = await response.json();

        if (documents.length === 0) {
            documentsContainer.innerHTML = '<div class="alert alert-info">You have not uploaded any documents yet.</div>';
            return;
        }

        // Build the HTML for the document list using Bootstrap's accordion component
        let documentsHtml = '<div class="accordion" id="documentsAccordion">';
        documents.forEach((doc, index) => {
            const uploadDate = new Date(doc.upload_timestamp + 'Z').toLocaleString();
            documentsHtml += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${index}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                            <strong>${doc.filename}</strong>&nbsp;-&nbsp;<small class="text-muted">Uploaded on ${uploadDate}</small>
                        </button>
                    </h2>
                    <div id="collapse${index}" class="accordion-collapse collapse" data-bs-parent="#documentsAccordion">
                        <div class="accordion-body">
                            <h6>Extracted Text:</h6>
                            <pre class="bg-light p-2 rounded">${doc.ocr_text || 'No text extracted.'}</pre>
                            <button class="btn btn-sm btn-danger mt-2 delete-btn" data-id="${doc.id}">Delete Document</button>
                        </div>
                    </div>
                </div>
            `;
        });
        documentsHtml += '</div>';
        documentsContainer.innerHTML = documentsHtml;

    } catch (error) {
        console.error('Error loading documents:', error);
        documentsContainer.innerHTML = '<div class="alert alert-danger">Could not load your documents.</div>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // The login check and navbar loading are handled by main.js
    loadDocuments();

    // Event listener to handle delete button clicks
    const documentsContainer = document.getElementById('documents-container');
    if (documentsContainer) {
        documentsContainer.addEventListener('click', async (e) => {
            if (e.target.classList.contains('delete-btn')) {
                const docId = e.target.dataset.id;
                
                // Ask for confirmation before deleting
                if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
                    try {
                        const response = await fetch(`${API_URL}/documents/${docId}`, {
                            method: 'DELETE',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });

                        if (!response.ok) {
                            throw new Error('Failed to delete document');
                        }
                        
                        // If deletion is successful, reload the list
                        loadDocuments();

                    } catch (error) {
                        console.error('Delete error:', error);
                        alert('Could not delete the document.');
                    }
                }
            }
        });
    }
});
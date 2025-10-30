// frontend/scripts/prediction.js
// NOTE: The global variables 'API_URL' and 'token' are defined in main.js

let activeInput = null;

// Finds all numbers in a block of text and wraps them in a clickable span
function processOcrText(text) {
  if (!text) return "No text found.";
  const regex = /(\d+\.?\d*)/g;
  return text.replace(regex, '<span class="clickable-ocr-number">$1</span>');
}

// --- Main script execution after the page is loaded ---
document.addEventListener("DOMContentLoaded", () => {
  // --- NEW: Initialize Bootstrap Popovers ---
  // This finds all elements with data-bs-toggle="popover" and activates them.
  const popoverTriggerList = document.querySelectorAll(
    '[data-bs-toggle="popover"]'
  );
  const popoverList = [...popoverTriggerList].map(
    (popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl)
  );
  // -----------------------------------------

  // NOTE: The initial login check and navbar loading are handled by main.js

  // Get references to all the important elements on the page.
  const predictionForm = document.getElementById("predictionForm");
  const uploadForm = document.getElementById("uploadForm");
  const resultDiv = document.getElementById("resultDiv");
  const uploadResultDiv = document.getElementById("uploadResultDiv");

  // Event listener to track which input field is currently active
  if (predictionForm) {
    predictionForm.addEventListener("focusin", (e) => {
      if (e.target.tagName === "INPUT") activeInput = e.target;
    });
  }

  // Event Listener for the Prediction Form submission
  if (predictionForm) {
    predictionForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      // We can reuse the spinner function from main.js
      if (typeof showSpinner === "function") showSpinner(submitButton);
      const formData = {
        age: parseInt(document.getElementById("age").value),
        sex: parseInt(document.getElementById("sex").value),
        cp: parseInt(document.getElementById("cp").value),
        trestbps: parseInt(document.getElementById("trestbps").value),
        chol: parseInt(document.getElementById("chol").value),
        fbs: parseInt(document.getElementById("fbs").value),
        restecg: parseInt(document.getElementById("restecg").value),
        thalach: parseInt(document.getElementById("thalach").value),
        exang: parseInt(document.getElementById("exang").value),
        oldpeak: parseFloat(document.getElementById("oldpeak").value),
        slope: parseInt(document.getElementById("slope").value),
        ca: parseInt(document.getElementById("ca").value),
        thal: parseInt(document.getElementById("thal").value),
      };

      try {
        const response = await fetch(`${API_URL}/predict`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
        const data = await response.json();

        if (response.ok) {
          let resultClass = "alert-success";
          if (data.risk_category === "Medium")
            resultClass = "alert-warning text-dark";
          if (data.risk_category === "High") resultClass = "alert-danger";
          sessionStorage.setItem("predictionResult", JSON.stringify(data));
          window.location.href = "result.html";
        } else {
          // This assumes a 'handleApiError' function exists in main.js
          if (typeof handleApiError === "function") {
            handleApiError(resultDiv, data, response);
          } else {
            resultDiv.innerHTML = `<div class="alert alert-danger mt-4">${
              data.msg || data.message || "An error occurred."
            }</div>`;
          }
        }
        const resultData = await response.json();

        // --- 3. THIS IS THE CRITICAL STEP ---
        // Save the full result to localStorage
        localStorage.setItem("predictionResult", JSON.stringify(resultData));

        // --- 4. Now, redirect to the result page ---
        window.location.href = "result.html";
      } catch (error) {
        console.error("Network error during prediction:", error);
        resultDiv.innerHTML = `<div class="alert alert-danger mt-4">A network error occurred. Please try again.</div>`;
      } finally {
        if (typeof hideSpinner === "function") hideSpinner(submitButton);
      }
    });
  }

  // Event Listener for the File Upload Form
  if (uploadForm) {
    const fileInput = document.getElementById("documentFile");
    const uploadButton = document.getElementById("uploadButton");
    const dropZonePrompt = uploadForm.querySelector(".drop-zone__prompt");

    uploadForm.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) updateDropZonePrompt(fileInput.files[0]);
    });

    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) =>
      uploadForm.addEventListener(eventName, preventDefaults, false)
    );
    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }
    ["dragenter", "dragover"].forEach((eventName) =>
      uploadForm.addEventListener(
        eventName,
        () => uploadForm.classList.add("drop-zone--over"),
        false
      )
    );
    ["dragleave", "drop"].forEach((eventName) =>
      uploadForm.addEventListener(
        eventName,
        () => uploadForm.classList.remove("drop-zone--over"),
        false
      )
    );

    uploadForm.addEventListener("drop", (e) => {
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updateDropZonePrompt(fileInput.files[0]);
      }
    });

    function updateDropZonePrompt(file) {
      dropZonePrompt.innerHTML = `<strong>Selected file:</strong> ${file.name}`;
    }

    uploadButton.addEventListener("click", async () => {
      uploadResultDiv.innerHTML =
        '<div class="alert alert-info">Uploading...</div>';
      if (fileInput.files.length === 0) {
        uploadResultDiv.innerHTML =
          '<div class="alert alert-danger">Please select a file to upload.</div>';
        return;
      }
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("document", file);
      try {
        const response = await fetch(`${API_URL}/upload-document`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        const data = await response.json();
        if (response.ok) {
          const highlightedText = processOcrText(data.extracted_text);
          uploadResultDiv.innerHTML = `<div class="alert alert-success mt-4"><h4>Upload Successful!</h4><p><strong>Filename:</strong> ${data.filename}</p><p><strong>Extracted Text (click a number to fill the form):</strong></p><pre class="bg-white p-2 rounded">${highlightedText}</pre></div>`;
        } else {
          if (typeof handleApiError === "function") {
            handleApiError(uploadResultDiv, data, response);
          } else {
            uploadResultDiv.innerHTML = `<div class="alert alert-danger mt-4">${
              data.msg || data.message || "An error occurred."
            }</div>`;
          }
        }
      } catch (error) {
        console.error("Network error during upload:", error);
        uploadResultDiv.innerHTML = `<div class="alert alert-danger mt-4">A network error occurred. Please try again.</div>`;
      }
    });
  }

  // Event listener to handle clicks on the clickable OCR numbers
  if (uploadResultDiv) {
    uploadResultDiv.addEventListener("click", (e) => {
      if (e.target.classList.contains("clickable-ocr-number") && activeInput) {
        activeInput.value = e.target.textContent;
        const formInputs = Array.from(predictionForm.querySelectorAll("input"));
        const currentIndex = formInputs.indexOf(activeInput);
        if (currentIndex !== -1 && currentIndex < formInputs.length - 1) {
          const nextInput = formInputs[currentIndex + 1];
          nextInput.focus();
        }
      }
    });
  }
});

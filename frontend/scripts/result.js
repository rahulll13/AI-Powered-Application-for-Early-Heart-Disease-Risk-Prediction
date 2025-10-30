// frontend/scripts/result.js

document.addEventListener("DOMContentLoaded", () => {
  // Retrieve the prediction data from the browser's session storage
  const resultDataString = sessionStorage.getItem("predictionResult");

  // If there's no result data, redirect back to the prediction page
  if (!resultDataString) {
    window.location.href = "prediction.html";
    return;
  }

  const resultData = JSON.parse(resultDataString);

  const riskCategoryText = document.getElementById("riskCategoryText");
  const probabilityText = document.getElementById("probabilityText");
  const canvas = document.getElementById("resultGauge");

  // Define colors for different risk levels
  const riskColors = {
    Low: "#198754", // Green
    Medium: "#ffc107", // Yellow
    High: "#dc3545", // Red
  };

  // Update the text on the page
  riskCategoryText.textContent = `${resultData.risk_category} Risk`;
  riskCategoryText.style.color = riskColors[resultData.risk_category];
  probabilityText.textContent = `Probability of Heart Disease: ${(
    resultData.probability * 100
  ).toFixed(2)}%`;

  // --- Gauge Chart Logic ---
  const opts = {
    angle: -0.2, // The span of the gauge arc
    lineWidth: 0.2, // The line thickness
    radiusScale: 1, // Relative radius
    pointer: {
      length: 0.6, // Relative pointer length
      strokeWidth: 0.035, // The thickness
      color: "#000000", // Fill color
    },
    limitMax: false, // If false, max value increases automatically if value > maxValue
    limitMin: false, // If true, the min value of the gauge will be fixed
    colorStart: "#6FADCF", // Colors
    colorStop: riskColors[resultData.risk_category], // The color of the gauge will match the risk
    strokeColor: "#E0E0E0", // Rest of the arc
    generateGradient: true,
    highDpiSupport: true,
    staticLabels: {
      font: "12px sans-serif", // Specifies font
      labels: [0, 25, 50, 75, 100], // Print labels at these values
      color: "#000000", // Optional: Label color
      fractionDigits: 0, // Optional: Numerical precision. 0=round off.
    },
  };

  const target = document.getElementById("resultGauge");
  const gauge = new Gauge(target).setOptions(opts);
  gauge.maxValue = 100; // Set max value of the gauge
  gauge.setMinValue(0); // Set min value
  gauge.animationSpeed = 32; // Set animation speed (32 is default)
  gauge.set(resultData.probability * 100); // Set the value

  // Clean up the session storage so the page doesn't show old data on refresh
  sessionStorage.removeItem("predictionResult");

  // --- === NEW: POPULATE THE EXPLANATIONS === ---
  // --- === UPDATED: POPULATE THE EXPLANATIONS LIST === ---
  const explanationCard = document.getElementById("explanation-card");
  const explanationList = document.getElementById("explanation-list"); // Target the <ul>

  // Check if the list exists and if we have explanations
  if (
    explanationList &&
    explanationCard &&
    resultData.explanations &&
    resultData.explanations.length > 0
  ) {
    let explanationHtml = ""; // We are only building the list items

    // Loop through the top 5 explanations
    resultData.explanations.slice(0, 5).forEach((exp) => {
      const isNegative = exp.impact < 0; // Negative impact means *decreased* risk
      const colorClass = isNegative ? "text-success" : "text-danger";
      const icon = isNegative ? "&#9660;" : "&#9650;"; // Down arrow or Up arrow

      explanationHtml += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span>
                        <strong>${exp.feature}</strong>: 
                        <span class="text-muted">${exp.description}</span>
                    </span>
                    <span class="${colorClass} fs-5 fw-bold" style="white-space: nowrap;">
                        ${icon}
                    </span>
                </li>
            `;
    });

    explanationList.innerHTML = explanationHtml; // Inject the <li> elements into the <ul>
  } else {
    // No explanations, so hide the entire second card
    if (explanationCard) {
      explanationCard.style.display = "none";
    }
    console.warn(
      "Explanation list not found or no explanations in result data."
    );
  }

  // --- === NEW: POPULATE RECOMMENDATIONS LIST === ---
  const recommendationList = document.getElementById("recommendation-list");
  const recommendationTitle = document.getElementById("rec-title");

  if (
    recommendationList &&
    recommendationTitle &&
    resultData.recommendations &&
    resultData.recommendations.length > 0
  ) {
    // Show the title
    recommendationTitle.classList.remove("d-none");

    let recommendationHtml = "";
    resultData.recommendations.forEach((rec) => {
      recommendationHtml += `
                <li class="list-group-item">
                    <p class="mb-1"><strong>Based on ${rec.feature}:</strong></p>
                    <p class="mb-0 text-muted">${rec.advice}</p>
                </li>
            `;
    });
    recommendationList.innerHTML = recommendationHtml;
  } else {
    // If no recommendations, make sure the section is hidden
    if (document.getElementById("recommendation-section")) {
      document.getElementById("recommendation-section").style.display = "none";
    }
  }

  // Clean up the session storage
  sessionStorage.removeItem("predictionResult");
});

const API_BASE = window.location.origin;
let allProgrammes = [];

document.addEventListener("DOMContentLoaded", async () => {
  // Load programmes
  await loadProgrammes();
  
  // Check URL params for pre-selected programme
  const urlParams = new URLSearchParams(window.location.search);
  const programmeName = urlParams.get("programme");
  if (programmeName) {
    document.getElementById("programme_name").value = programmeName;
  }

  // Handle form submission
  document.getElementById("monitoring-form").addEventListener("submit", handleFormSubmit);
});

async function loadProgrammes() {
  try {
    const response = await fetch(`${API_BASE}/programmes/`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) throw new Error("Failed to load programmes");

    allProgrammes = await response.json();
    const select = document.getElementById("programme_name");
    
    allProgrammes.forEach((prog) => {
      const option = document.createElement("option");
      option.value = prog.name;
      option.textContent = prog.name;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Error loading programmes:", err);
    showError("Failed to load programmes. Please refresh the page.");
  }
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const formData = {
    programme_name: document.getElementById("programme_name").value,
    focal_department: document.getElementById("focal_department").value,
    focal_aide_hm: document.getElementById("focal_aide_hm").value,
    focal_ministry_official: document.getElementById("focal_ministry_official").value,
    reporting_month: document.getElementById("reporting_month").value + "-01",
    programme_launch_date: document.getElementById("programme_launch_date").value || null,
    total_youth_registered: parseInt(document.getElementById("total_youth_registered").value) || 0,
    youth_trained: parseInt(document.getElementById("youth_trained").value) || 0,
    youth_funded: parseInt(document.getElementById("youth_funded").value) || 0,
    youth_with_outcomes: parseInt(document.getElementById("youth_with_outcomes").value) || 0,
    partnerships: document.getElementById("partnerships").value,
    challenges: document.getElementById("challenges").value,
    mitigation_strategies: document.getElementById("mitigation_strategies").value,
    scale_up_plans: document.getElementById("scale_up_plans").value,
    success_story: document.getElementById("success_story").value,
  };

  try {
    const response = await fetch(`${API_BASE}/reports/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(formData),
    });

    console.log("Response status:", response.status);
    
    let data;
    try {
      data = await response.json();
    } catch (parseErr) {
      console.error("Failed to parse response as JSON:", parseErr);
      const text = await response.text();
      console.error("Response text:", text);
      throw new Error("Failed to parse server response");
    }

    if (!response.ok) {
      throw new Error(data.detail || data.message || "Failed to submit report");
    }

    console.log("Report submitted successfully:", data);

    // Show success message
    const successMsg = document.getElementById("success-message");
    successMsg.innerHTML = "✅ Report submitted successfully! Redirecting to your dashboard...";
    successMsg.style.display = "block";
    document.getElementById("error-message").style.display = "none";
    document.getElementById("monitoring-form").reset();

    // Redirect to dashboard after 2 seconds
    setTimeout(() => {
      window.location.href = "/admin.html";
    }, 2000);
  } catch (err) {
    console.error("Error submitting report:", err);
    showError(err.message || "An error occurred while submitting your report");
  }
}

function showError(message) {
  const errorDiv = document.getElementById("error-message");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function goBack() {
  window.history.back();
}

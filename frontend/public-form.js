const API_BASE = window.location.origin;
const EMAILJS_CONFIG = window.EMAILJS_CONFIG || {};
let emailjsReady = false;

function isEmailJSConfigured() {
  return (
    EMAILJS_CONFIG &&
    typeof EMAILJS_CONFIG.serviceId === "string" &&
    EMAILJS_CONFIG.serviceId.trim() &&
    typeof EMAILJS_CONFIG.templateId === "string" &&
    EMAILJS_CONFIG.templateId.trim() &&
    typeof EMAILJS_CONFIG.publicKey === "string" &&
    EMAILJS_CONFIG.publicKey.trim() &&
    typeof EMAILJS_CONFIG.adminEmail === "string" &&
    EMAILJS_CONFIG.adminEmail.trim()
  );
}

function initEmailJS() {
  if (emailjsReady) return;
  if (!window.emailjs) return;
  if (!isEmailJSConfigured()) return;
  window.emailjs.init({ publicKey: EMAILJS_CONFIG.publicKey });
  emailjsReady = true;
}

async function sendAdminNotification({ subject, message }) {
  if (!window.emailjs) return;
  if (!isEmailJSConfigured()) return;
  initEmailJS();

  const templateParams = {
    to_email: EMAILJS_CONFIG.adminEmail,
    subject,
    message,
  };

  await window.emailjs.send(
    EMAILJS_CONFIG.serviceId,
    EMAILJS_CONFIG.templateId,
    templateParams,
  );
}

function getToken() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("token");
}

function getProgrammeId() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[parts.length - 1];
}

document.addEventListener("DOMContentLoaded", async () => {
  const token = getToken();
  const programmeId = getProgrammeId();

  if (!token || !programmeId) {
    showError("Missing or invalid access token.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/forms/${programmeId}/info?token=${encodeURIComponent(token)}`);
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to load form info");
    }
    const info = await response.json();
    document.getElementById("programme_name").value = info.programme_name || "";
  } catch (err) {
    console.error("Error loading form info:", err);
    showError(err.message || "Failed to load form info.");
    return;
  }

  document.getElementById("monitoring-form").addEventListener("submit", handleFormSubmit);
});

async function handleFormSubmit(e) {
  e.preventDefault();

  const token = getToken();
  const programmeId = getProgrammeId();

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
    const response = await fetch(`${API_BASE}/forms/${programmeId}/submit?token=${encodeURIComponent(token)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to submit report");
    }

    const successMsg = document.getElementById("success-message");
    successMsg.innerHTML = "Report submitted successfully. Thank you.";
    successMsg.style.display = "block";
    document.getElementById("error-message").style.display = "none";
    document.getElementById("monitoring-form").reset();

    const subject = `New Form Submission: ${formData.programme_name}`;
    const message = [
      "Hello Admin,",
      "",
      "A new form submission has been received.",
      "",
      `Programme: ${formData.programme_name}`,
      `Department: ${formData.focal_department || "N/A"}`,
      `Reporting Month: ${formData.reporting_month}`,
      `Total Registered: ${formData.total_youth_registered}`,
      `Youth Trained: ${formData.youth_trained}`,
      `Youth Funded: ${formData.youth_funded}`,
      `Youth With Outcomes: ${formData.youth_with_outcomes}`,
      "",
      "Please review it in the admin dashboard.",
    ].join("\n");

    try {
      await sendAdminNotification({ subject, message });
    } catch (err) {
      console.warn("Admin email notification failed:", err);
    }
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

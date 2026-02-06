const API_BASE = window.location.origin; // Use same origin as frontend
let programmesCache = [];

function isMobileView() {
  return window.matchMedia("(max-width: 768px)").matches;
}

async function loadAdminDashboard() {
  try {
    // Load stats
    await loadStats();
    // Load all reports
    await loadAllReports();
    // Load programmes
    await loadProgrammes();
    // Load form submissions
    await loadFormSubmissions();
  } catch (err) {
    console.error("Error loading admin dashboard:", err);
    showError("Failed to load admin dashboard. Please refresh the page.");
  }
}

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/reports/dashboard`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const stats = await response.json();
    const container = document.getElementById("stats-container");

    container.innerHTML = `
      <div class="stat-card">
        <h3>Total Youth Registered</h3>
        <div class="value">${stats.total_youth_registered || 0}</div>
      </div>
      <div class="stat-card">
        <h3>Youth Trained</h3>
        <div class="value">${stats.total_trained || 0}</div>
      </div>
      <div class="stat-card">
        <h3>Training Percentage</h3>
        <div class="value">${stats.training_percentage || 0}%</div>
      </div>
      <div class="stat-card">
        <h3>Youth Funded</h3>
        <div class="value">${stats.total_youth_funded || 0}</div>
      </div>
      <div class="stat-card">
        <h3>Youth with Outcomes</h3>
        <div class="value">${stats.total_youth_with_outcomes || 0}</div>
      </div>
      <div class="stat-card">
        <h3>Total Reports</h3>
        <div class="value">${stats.total_reports || 0}</div>
      </div>
    `;
  } catch (err) {
    console.error("Error loading stats:", err);
    showError("Failed to load statistics.");
  }
}

async function loadAllReports() {
  try {
    const response = await fetch(`${API_BASE}/reports/`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = "/";
        return;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reports = await response.json();
    const container = document.getElementById("reports-container");

    if (reports.length === 0) {
      container.innerHTML = "<div class='no-data'>No reports available.</div>";
      return;
    }

    if (isMobileView()) {
      const cards = reports.map((r) => `
        <div class="admin-card">
          <h4>${r.programme_name}</h4>
          <div class="admin-field"><label>Reporting Month</label>${r.reporting_month || "N/A"}</div>
          <div class="admin-field"><label>Total Registered</label>${r.total_youth_registered || 0}</div>
          <div class="admin-field"><label>Trained</label>${r.youth_trained || 0}</div>
          <div class="admin-field"><label>Funded</label>${r.youth_funded || 0}</div>
          <div class="admin-field"><label>Outcomes</label>${r.youth_with_outcomes || 0}</div>
          <div class="admin-field"><label>Department</label>${r.focal_department || "N/A"}</div>
          <div class="admin-field"><label>Challenges</label>${r.challenges ? r.challenges.substring(0, 80) + "..." : "N/A"}</div>
          <div class="admin-field"><label>Submitted Date</label>${r.created_at ? new Date(r.created_at).toLocaleDateString() : "N/A"}</div>
        </div>
      `).join("");
      container.innerHTML = `<div class="admin-cards">${cards}</div>`;
      return;
    }

    const rows = reports.map((r) => `
      <tr>
        <td><strong>${r.programme_name}</strong></td>
        <td>${r.reporting_month || "N/A"}</td>
        <td>${r.total_youth_registered || 0}</td>
        <td>${r.youth_trained || 0}</td>
        <td>${r.youth_funded || 0}</td>
        <td>${r.youth_with_outcomes || 0}</td>
        <td>${r.focal_department || "N/A"}</td>
        <td>${r.challenges ? r.challenges.substring(0, 50) + "..." : "N/A"}</td>
        <td>${r.created_at ? new Date(r.created_at).toLocaleDateString() : "N/A"}</td>
      </tr>
    `).join("");

    container.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Programme</th>
            <th>Reporting Month</th>
            <th>Total Registered</th>
            <th>Trained</th>
            <th>Funded</th>
            <th>Outcomes</th>
            <th>Department</th>
            <th>Challenges</th>
            <th>Submitted Date</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;
  } catch (err) {
    console.error("Error loading reports:", err);
    showError("Failed to load reports.");
  }
}

async function loadProgrammes() {
  try {
    const [programmesResponse, summaryResponse] = await Promise.all([
      fetch(`${API_BASE}/programmes/`, { method: "GET", credentials: "include" }),
      fetch(`${API_BASE}/forms/admin/summary`, { method: "GET", credentials: "include" }),
    ]);

    if (!programmesResponse.ok) {
      throw new Error(`HTTP error! status: ${programmesResponse.status}`);
    }
    if (!summaryResponse.ok) {
      throw new Error(`HTTP error! status: ${summaryResponse.status}`);
    }

    const programmes = await programmesResponse.json();
    const summary = await summaryResponse.json();
    programmesCache = programmes;
    const summaryMap = new Map(summary.map((s) => [s.programme_id, s]));
    const container = document.getElementById("programmes-container");

    if (programmes.length === 0) {
      container.innerHTML = "<div class='no-data'>No programmes available.</div>";
      return;
    }

    populateFormFilter(programmes);

    if (isMobileView()) {
      const cards = programmes.map((p) => {
        const stats = summaryMap.get(p.id) || { submission_count: 0, last_submitted_at: null };
        const lastSubmitted = stats.last_submitted_at ? new Date(stats.last_submitted_at).toLocaleString() : "N/A";
        return `
          <div class="admin-card">
            <h4>${p.name}</h4>
            <div class="admin-field"><label>Department</label>${p.department || "Unspecified"}</div>
            <div class="admin-field">
              <label>Description</label>
              <input type="text" id="desc-${p.id}" value="${p.description || ""}" placeholder="Description" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;" />
            </div>
            <div class="admin-field">
              <label>Recipient Email</label>
              <input type="email" id="email-${p.id}" value="${p.recipient_email || ""}" placeholder="Recipient email" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;" />
            </div>
            <div class="admin-field"><label>Submission Count</label>${stats.submission_count || 0}</div>
            <div class="admin-field"><label>Last Submitted</label>${lastSubmitted}</div>
            <div class="admin-actions">
              <button onclick="saveProgramme(${p.id})" style="background: #006400; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer;">Save</button>
              <button onclick="sendFormLink(${p.id})" style="background: #004d00; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer;">Send Link</button>
            </div>
          </div>
        `;
      }).join("");
      container.innerHTML = `<div class="admin-cards">${cards}</div>`;
      return;
    }

    const rows = programmes.map((p) => `
      ${(() => {
        const stats = summaryMap.get(p.id) || { submission_count: 0, last_submitted_at: null };
        const lastSubmitted = stats.last_submitted_at ? new Date(stats.last_submitted_at).toLocaleString() : "N/A";
        return `
      <tr>
        <td><strong>${p.name}</strong></td>
        <td>${p.department || "Unspecified"}</td>
        <td>
          <input type="text" id="desc-${p.id}" value="${p.description || ""}" placeholder="Description" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;" />
        </td>
        <td>
          <input type="email" id="email-${p.id}" value="${p.recipient_email || ""}" placeholder="Recipient email" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;" />
        </td>
        <td>${stats.submission_count || 0}</td>
        <td>${lastSubmitted}</td>
        <td style="white-space: nowrap;">
          <button onclick="saveProgramme(${p.id})" style="background: #006400; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; margin-right: 6px;">Save</button>
          <button onclick="sendFormLink(${p.id})" style="background: #004d00; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer;">Send Link</button>
        </td>
      </tr>
        `;
      })()}
    `).join("");

    container.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Programme Name</th>
            <th>Department</th>
            <th>Description</th>
            <th>Recipient Email</th>
            <th>Submission Count</th>
            <th>Last Submitted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;
  } catch (err) {
    console.error("Error loading programmes:", err);
    showError("Failed to load programmes.");
  }
}

function populateFormFilter(programmes) {
  const select = document.getElementById("form-submissions-filter");
  if (!select) return;

  select.innerHTML = `<option value="">All Programmes</option>` + programmes.map((p) => `
    <option value="${p.id}">${p.name}</option>
  `).join("");
}

async function saveProgramme(programmeId) {
  const description = document.getElementById(`desc-${programmeId}`)?.value || "";
  const recipientEmail = document.getElementById(`email-${programmeId}`)?.value || "";

  if (!recipientEmail) {
    showError("Recipient email is required.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/programmes/${programmeId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ description, recipient_email: recipientEmail }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to update programme");
    }

    showMessage("Programme updated successfully.");
    await loadProgrammes();
  } catch (err) {
    console.error("Error updating programme:", err);
    showError(err.message || "Failed to update programme.");
  }
}

async function sendFormLink(programmeId) {
  const recipientEmail = document.getElementById(`email-${programmeId}`)?.value?.trim() || "";
  if (!recipientEmail) {
    showError("Recipient email is required before sending the link.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/forms/admin/send-link`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ programme_id: programmeId, recipient_email: recipientEmail }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to send form link");
    }

    showMessage("Form link sent successfully.");
  } catch (err) {
    console.error("Error sending form link:", err);
    showError(err.message || "Failed to send form link.");
  }
}

async function loadFormSubmissions() {
  try {
    const programmeId = document.getElementById("form-submissions-filter")?.value || "";
    const query = programmeId ? `?programme_id=${encodeURIComponent(programmeId)}` : "";
    const response = await fetch(`${API_BASE}/forms/admin/submissions${query}`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const submissions = await response.json();
    const container = document.getElementById("form-submissions-container");

    if (submissions.length === 0) {
      container.innerHTML = "<div class='no-data'>No form submissions yet.</div>";
      return;
    }

    if (isMobileView()) {
      const cards = submissions.map((s) => `
        <div class="admin-card">
          <h4>${programmeMap.get(s.programme_id) || s.programme_id || "N/A"}</h4>
          <div class="admin-field"><label>Recipient Email</label>${s.recipient_email}</div>
          <div class="admin-field"><label>Submitted At</label>${s.submitted_at ? new Date(s.submitted_at).toLocaleString() : "N/A"}</div>
          <div class="admin-field"><label>Form Data</label><pre style="white-space: pre-wrap; margin: 0;">${JSON.stringify(s.form_data, null, 2)}</pre></div>
        </div>
      `).join("");
      container.innerHTML = `<div class="admin-cards">${cards}</div>`;
      return;
    }

    const programmeMap = new Map(programmesCache.map((p) => [p.id, p.name]));
    const rows = submissions.map((s) => `
      <tr>
        <td>${programmeMap.get(s.programme_id) || s.programme_id || "N/A"}</td>
        <td>${s.recipient_email}</td>
        <td>${s.submitted_at ? new Date(s.submitted_at).toLocaleString() : "N/A"}</td>
        <td><pre style="white-space: pre-wrap; max-width: 420px;">${JSON.stringify(s.form_data, null, 2)}</pre></td>
      </tr>
    `).join("");

    container.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Programme</th>
            <th>Recipient Email</th>
            <th>Submitted At</th>
            <th>Form Data</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;
  } catch (err) {
    console.error("Error loading form submissions:", err);
    showError("Failed to load form submissions.");
  }
}

function showError(message) {
  const container = document.getElementById("error-container");
  container.innerHTML = `<div class="error-message">${message}</div>`;
}

function showMessage(message) {
  const container = document.getElementById("error-container");
  container.innerHTML = `<div class="success-message" style="display:block;">${message}</div>`;
}

async function logout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch (err) {
    console.error("Error during logout:", err);
  }

  // Clear any stored data and redirect to login
  window.location.href = "/";
}

// Load admin dashboard on page load
document.addEventListener("DOMContentLoaded", () => {
  loadAdminDashboard();
});

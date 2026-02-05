const API_BASE = window.location.origin; // Use same origin as frontend

async function loadDashboard() {
  // Check if user is authenticated (session cookie exists)
  try {
    // Load stats
    await loadStats();
    // Load programmes
    await loadProgrammes();
    // Load reports
    await loadReports();
  } catch (err) {
    console.error("Error loading dashboard:", err);
    showError("Failed to load dashboard. Please refresh the page.");
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

async function loadProgrammes() {
  try {
    const response = await fetch(`${API_BASE}/programmes/`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const programmes = await response.json();
    const container = document.getElementById("programmes-container");

    if (programmes.length === 0) {
      container.innerHTML = "<div class='no-data'>No programmes available.</div>";
      return;
    }

    const list = programmes.map((p) => `
      <li>
        <a href="/report-form.html?programme=${encodeURIComponent(p.name)}" style="text-decoration: none; color: inherit; display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <div>
            <span class="programme-name">${p.name}</span>
            <span class="programme-dept">${p.department}</span>
          </div>
          <span style="color: #006400; font-weight: bold; margin-left: 10px;">→ Submit Report</span>
        </a>
      </li>
    `).join("");

    container.innerHTML = `<ul class="programmes-list">${list}</ul>`;
  } catch (err) {
    console.error("Error loading programmes:", err);
    showError("Failed to load programmes.");
  }
}

async function loadReports() {
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
      container.innerHTML = "<div class='no-data'>No reports submitted yet.</div>";
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
      </tr>
    `).join("");

    container.innerHTML = `
      <table class="reports-table">
        <thead>
          <tr>
            <th>Programme</th>
            <th>Reporting Month</th>
            <th>Total Registered</th>
            <th>Trained</th>
            <th>Funded</th>
            <th>Outcomes</th>
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

function showError(message) {
  const container = document.getElementById("error-container");
  container.innerHTML = `<div class="error-message">${message}</div>`;
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

// Load dashboard on page load
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
});

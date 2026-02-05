const API_BASE = window.location.origin;
let chartsRegistry = {};
let analyticsData = {};

document.addEventListener("DOMContentLoaded", async () => {
  Chart.register(ChartDataLabels);
  await loadAnalytics();
  populateMonthFilter();
});

async function loadAnalytics() {
  try {
    // Fetch all reports
    const response = await fetch(`${API_BASE}/reports/`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reports = await response.json();
    analyticsData = processReportsData(reports);

    // Render stats
    renderStats();

    // Render charts
    renderCharts();
  } catch (err) {
    console.error("Error loading analytics:", err);
    showError("Failed to load analytics data. Please refresh the page.");
  }
}

function processReportsData(reports) {
  const data = {
    totalRegistered: 0,
    totalTrained: 0,
    totalFunded: 0,
    totalOutcomes: 0,
    monthlyData: {},
    departmentData: {},
    partnersData: { private: 0, ngo: 0, government: 0, academic: 0 },
    submitCount: reports.length,
  };

  reports.forEach((report) => {
    data.totalRegistered += report.total_youth_registered || 0;
    data.totalTrained += report.youth_trained || 0;
    data.totalFunded += report.youth_funded || 0;
    data.totalOutcomes += report.youth_with_outcomes || 0;

    // Monthly tracking
    const month = report.reporting_month?.substring(0, 7) || "Unknown";
    if (!data.monthlyData[month]) {
      data.monthlyData[month] = {
        registered: 0,
        trained: 0,
        funded: 0,
        outcomes: 0,
      };
    }
    data.monthlyData[month].registered += report.total_youth_registered || 0;
    data.monthlyData[month].trained += report.youth_trained || 0;
    data.monthlyData[month].funded += report.youth_funded || 0;
    data.monthlyData[month].outcomes += report.youth_with_outcomes || 0;

    // Department tracking
    const dept = report.focal_department || "Unknown";
    if (!data.departmentData[dept]) {
      data.departmentData[dept] = {
        reports: 0,
        registered: 0,
        trained: 0,
      };
    }
    data.departmentData[dept].reports += 1;
    data.departmentData[dept].registered += report.total_youth_registered || 0;
    data.departmentData[dept].trained += report.youth_trained || 0;

    // Partnerships
    if (report.partnerships) {
      const partnerships = report.partnerships.split(",").map((p) => p.trim());
      partnerships.forEach((p) => {
        if (p.includes("Private")) data.partnersData.private++;
        if (p.includes("NGO")) data.partnersData.ngo++;
        if (p.includes("Government")) data.partnersData.government++;
        if (p.includes("Academic")) data.partnersData.academic++;
      });
    }
  });

  return data;
}

function renderStats() {
  const trainingPct =
    analyticsData.totalRegistered > 0
      ? ((analyticsData.totalTrained / analyticsData.totalRegistered) * 100).toFixed(1)
      : 0;

  const outcomePct =
    analyticsData.totalTrained > 0
      ? ((analyticsData.totalOutcomes / analyticsData.totalTrained) * 100).toFixed(1)
      : 0;

  const statsHTML = `
    <div class="stat-card-analytics">
      <h4>Total Youth Registered</h4>
      <div class="value">${analyticsData.totalRegistered}</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Youth Trained</h4>
      <div class="value">${analyticsData.totalTrained}</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Training Rate</h4>
      <div class="value">${trainingPct}%</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Youth Funded</h4>
      <div class="value">${analyticsData.totalFunded}</div>
    </div>
    <div class="stat-card-analytics">
      <h4>With Outcomes</h4>
      <div class="value">${analyticsData.totalOutcomes}</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Outcome Rate</h4>
      <div class="value">${outcomePct}%</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Reports Submitted</h4>
      <div class="value">${analyticsData.submitCount}</div>
    </div>
    <div class="stat-card-analytics">
      <h4>Departments Active</h4>
      <div class="value">${Object.keys(analyticsData.departmentData).length}</div>
    </div>
  `;

  document.getElementById("stats-grid").innerHTML = statsHTML;
}

function renderCharts() {
  // Youth Pipeline Chart
  renderPipelineChart();

  // Training Efficiency Chart
  renderTrainingChart();

  // Outcomes Chart
  renderOutcomesChart();

  // Partnerships Chart
  renderPartnershipsChart();

  // Trend Chart
  renderTrendChart();

  // Submission Status Chart
  renderSubmissionChart();

  // Department Chart
  renderDepartmentChart();
}

function renderPipelineChart() {
  const ctx = document.getElementById("pipelineChart").getContext("2d");

  if (chartsRegistry.pipeline) chartsRegistry.pipeline.destroy();

  chartsRegistry.pipeline = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Registered", "Trained", "Funded", "Outcomes"],
      datasets: [
        {
          label: "Youth Pipeline",
          data: [
            analyticsData.totalRegistered,
            analyticsData.totalTrained,
            analyticsData.totalFunded,
            analyticsData.totalOutcomes,
          ],
          backgroundColor: ["#006400", "#28a745", "#ffc107", "#17a2b8"],
          borderColor: ["#004d00", "#1e7e34", "#e0a800", "#138496"],
          borderWidth: 2,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#000",
          font: { weight: "bold" },
          anchor: "end",
          align: "top",
        },
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
}

function renderTrainingChart() {
  const ctx = document.getElementById("trainingChart").getContext("2d");

  if (chartsRegistry.training) chartsRegistry.training.destroy();

  const untrained =
    analyticsData.totalRegistered - analyticsData.totalTrained;

  chartsRegistry.training = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Trained", "Not Yet Trained"],
      datasets: [
        {
          data: [analyticsData.totalTrained, untrained],
          backgroundColor: ["#28a745", "#dc3545"],
          borderColor: ["#1e7e34", "#c82333"],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#fff",
          font: { weight: "bold", size: 14 },
        },
        legend: { position: "bottom" },
      },
    },
  });
}

function renderOutcomesChart() {
  const ctx = document.getElementById("outcomesChart").getContext("2d");

  if (chartsRegistry.outcomes) chartsRegistry.outcomes.destroy();

  const withoutOutcomes =
    analyticsData.totalTrained - analyticsData.totalOutcomes;

  chartsRegistry.outcomes = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["With Outcomes", "Without Outcomes"],
      datasets: [
        {
          data: [analyticsData.totalOutcomes, withoutOutcomes],
          backgroundColor: ["#006400", "#e9ecef"],
          borderColor: ["#004d00", "#adb5bd"],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#000",
          font: { weight: "bold", size: 12 },
        },
        legend: { position: "bottom" },
      },
    },
  });
}

function renderPartnershipsChart() {
  const ctx = document.getElementById("partnershipsChart").getContext("2d");

  if (chartsRegistry.partnerships)
    chartsRegistry.partnerships.destroy();

  chartsRegistry.partnerships = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Private Sector", "NGOs", "Government", "Academic"],
      datasets: [
        {
          label: "Partnerships",
          data: [
            analyticsData.partnersData.private,
            analyticsData.partnersData.ngo,
            analyticsData.partnersData.government,
            analyticsData.partnersData.academic,
          ],
          backgroundColor: "#006400",
          borderColor: "#004d00",
          borderWidth: 2,
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#000",
          font: { weight: "bold" },
          anchor: "end",
          align: "right",
        },
        legend: { display: false },
      },
      scales: {
        x: { beginAtZero: true },
      },
    },
  });
}

function renderTrendChart() {
  const ctx = document.getElementById("trendChart").getContext("2d");

  if (chartsRegistry.trend) chartsRegistry.trend.destroy();

  const months = Object.keys(analyticsData.monthlyData).sort();
  const registered = months.map((m) => analyticsData.monthlyData[m].registered);
  const trained = months.map((m) => analyticsData.monthlyData[m].trained);
  const funded = months.map((m) => analyticsData.monthlyData[m].funded);

  chartsRegistry.trend = new Chart(ctx, {
    type: "line",
    data: {
      labels: months,
      datasets: [
        {
          label: "Registered",
          data: registered,
          borderColor: "#006400",
          backgroundColor: "rgba(0, 100, 0, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Trained",
          data: trained,
          borderColor: "#28a745",
          backgroundColor: "rgba(40, 167, 69, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Funded",
          data: funded,
          borderColor: "#ffc107",
          backgroundColor: "rgba(255, 193, 7, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: { display: false },
        legend: { position: "bottom" },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
}

function renderSubmissionChart() {
  const ctx = document.getElementById("submissionChart").getContext("2d");

  if (chartsRegistry.submission) chartsRegistry.submission.destroy();

  const submitted = analyticsData.submitCount;
  const pending = Math.max(0, Object.keys(analyticsData.departmentData).length * 3 - submitted);

  chartsRegistry.submission = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Submitted", "Pending"],
      datasets: [
        {
          data: [submitted, pending],
          backgroundColor: ["#28a745", "#ffc107"],
          borderColor: ["#1e7e34", "#e0a800"],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#fff",
          font: { weight: "bold", size: 14 },
        },
        legend: { position: "bottom" },
      },
    },
  });
}

function renderDepartmentChart() {
  const ctx = document.getElementById("departmentChart").getContext("2d");

  if (chartsRegistry.department) chartsRegistry.department.destroy();

  const departments = Object.keys(analyticsData.departmentData);
  const reports = departments.map((d) => analyticsData.departmentData[d].reports);

  chartsRegistry.department = new Chart(ctx, {
    type: "bar",
    data: {
      labels: departments,
      datasets: [
        {
          label: "Reports Submitted",
          data: reports,
          backgroundColor: "#006400",
          borderColor: "#004d00",
          borderWidth: 2,
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          color: "#000",
          font: { weight: "bold" },
          anchor: "end",
          align: "right",
        },
        legend: { display: false },
      },
      scales: {
        x: { beginAtZero: true },
      },
    },
  });
}

function populateMonthFilter() {
  const months = Object.keys(analyticsData.monthlyData).sort().reverse();
  const select = document.getElementById("month-filter");

  months.forEach((month) => {
    const option = document.createElement("option");
    option.value = month;
    option.textContent = month;
    select.appendChild(option);
  });
}

async function applyFilters() {
  // For now, this function just reloads all data
  // In future, can add specific month filtering
  await loadAnalytics();
}

async function exportToExcel() {
  try {
    // Simple CSV export
    let csv = "Monthly Report Analytics\n\n";

    csv += "Summary Statistics\n";
    csv += "Total Registered,Total Trained,Total Funded,Total with Outcomes\n";
    csv += `${analyticsData.totalRegistered},${analyticsData.totalTrained},${analyticsData.totalFunded},${analyticsData.totalOutcomes}\n\n`;

    csv += "Monthly Trends\n";
    csv += "Month,Registered,Trained,Funded,Outcomes\n";
    Object.keys(analyticsData.monthlyData)
      .sort()
      .forEach((month) => {
        const m = analyticsData.monthlyData[month];
        csv += `${month},${m.registered},${m.trained},${m.funded},${m.outcomes}\n`;
      });

    csv += "\nDepartment Performance\n";
    csv += "Department,Reports,Registered,Trained\n";
    Object.keys(analyticsData.departmentData).forEach((dept) => {
      const d = analyticsData.departmentData[dept];
      csv += `${dept},${d.reports},${d.registered},${d.trained}\n`;
    });

    // Download CSV
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `DMT-Analytics-${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
  } catch (err) {
    console.error("Error exporting to Excel:", err);
    showError("Failed to export to Excel");
  }
}

async function exportToPDF() {
  try {
    const container = document.querySelector(".analytics-container");
    if (!container) {
      showError("Unable to export: analytics container not found.");
      return;
    }

    const { jsPDF } = window.jspdf || {};
    if (!jsPDF || !window.html2canvas) {
      showError("PDF libraries failed to load. Please refresh and try again.");
      return;
    }

    const canvas = await window.html2canvas(container, {
      scale: 2,
      useCORS: true,
      backgroundColor: "#ffffff",
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "pt", "a4");
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = pageWidth;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    const filename = `DMT-Analytics-${new Date().toISOString().split("T")[0]}.pdf`;
    pdf.save(filename);
  } catch (err) {
    console.error("Error exporting to PDF:", err);
    showError("Failed to export PDF. Please try again.");
  }
}

function showError(message) {
  const errorContainer = document.getElementById("error-container");
  errorContainer.textContent = message;
  errorContainer.style.display = "block";
  setTimeout(() => {
    errorContainer.style.display = "none";
  }, 5000);
}

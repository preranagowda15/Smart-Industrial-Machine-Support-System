// Inspection Metrics & Confusion Matrix Controller
document.addEventListener("DOMContentLoaded", () => {
  const metricRecall = document.getElementById("metric-defect-recall");
  const metricAccuracy = document.getElementById("metric-accuracy");
  const metricPrecision = document.getElementById("metric-precision");
  const metricTotal = document.getElementById("metric-total-samples");

  const cmTn = document.getElementById("cm-tn");
  const cmFp = document.getElementById("cm-fp");
  const cmFn = document.getElementById("cm-fn");
  const cmTp = document.getElementById("cm-tp");

  const samplesTbody = document.getElementById("samples-tbody");
  const filterClass = document.getElementById("filter-samples-class");
  const btnReEvaluate = document.getElementById("btn-re-evaluate");

  let allSamples = [];

  async function fetchMetrics() {
    try {
      const resp = await App.apiFetch("/api/inspections/metrics/");
      if (!resp.ok) throw new Error("Failed to compute metrics.");

      const data = await resp.json();
      renderDashboard(data);
    } catch (err) {
      alert("Error calculating metrics: " + err.message);
    }
  }

  function renderDashboard(data) {
    const m = data.metrics || {};
    
    // KPI Cards
    if (metricRecall) metricRecall.textContent = `${m.defect_recall_percent}%`;
    if (metricAccuracy) metricAccuracy.textContent = `${m.accuracy_percent}%`;
    if (metricPrecision) metricPrecision.textContent = `${m.precision_percent}%`;
    if (metricTotal) metricTotal.textContent = data.total_samples || 60;

    // Confusion Matrix cells
    if (cmTn) cmTn.textContent = m.true_negatives;
    if (cmFp) cmFp.textContent = m.false_positives;
    if (cmFn) cmFn.textContent = m.false_negatives;
    if (cmTp) cmTp.textContent = m.true_positives;

    // Samples Table
    allSamples = data.samples || [];
    renderSamplesTable(allSamples);
  }

  function renderSamplesTable(samples) {
    if (!samplesTbody) return;

    const filtered = filterClass && filterClass.value
      ? samples.filter(s => s.actual_label === filterClass.value)
      : samples;

    if (filtered.length === 0) {
      samplesTbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No samples match.</td></tr>`;
      return;
    }

    samplesTbody.innerHTML = filtered.map((s, idx) => {
      const actualBadge = s.actual_label === "Defective"
        ? `<span class="badge bg-danger-subtle text-danger border border-danger">Defective</span>`
        : `<span class="badge bg-success-subtle text-success border border-success">Normal</span>`;

      const predBadge = s.predicted_class === "Defective"
        ? `<span class="badge bg-danger">Defective</span>`
        : `<span class="badge bg-success">Normal</span>`;

      const outcomeBadge = s.is_correct
        ? `<span class="badge bg-success"><i class="bi bi-check-lg me-1"></i>Correct</span>`
        : `<span class="badge bg-danger"><i class="bi bi-x-lg me-1"></i>Mismatch</span>`;

      return `
        <tr>
          <td class="text-muted small">${idx + 1}</td>
          <td class="font-monospace small fw-bold">${s.relative_path || s.image_id}</td>
          <td>${actualBadge}</td>
          <td>${predBadge}</td>
          <td class="fw-semibold text-dark">${(s.confidence * 100).toFixed(1)}%</td>
          <td class="font-monospace small">${s.defect_probability !== null ? s.defect_probability.toFixed(4) : "-"}</td>
          <td>${outcomeBadge}</td>
        </tr>
      `;
    }).join("");
  }

  if (filterClass) {
    filterClass.addEventListener("change", () => {
      renderSamplesTable(allSamples);
    });
  }

  if (btnReEvaluate) {
    btnReEvaluate.addEventListener("click", () => {
      fetchMetrics();
    });
  }

  // Initial load
  fetchMetrics();
});


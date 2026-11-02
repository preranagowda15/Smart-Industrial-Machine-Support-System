// Supervisor & Admin Dashboard Controller
document.addEventListener("DOMContentLoaded", () => {
  const supervisorContainer = document.getElementById("supervisor-dashboard-container");
  if (!supervisorContainer) return;

  async function loadSupervisorMetrics() {
    try {
      const resp = await App.apiFetch("/api/supervisor/metrics/");
      if (!resp || !resp.ok) return;
      const data = await resp.json();

      const m = data.metrics;
      document.getElementById("metric-total-questions").textContent = m.total_questions;
      document.getElementById("metric-answered-questions").textContent = m.answered_questions;
      document.getElementById("metric-insufficient-questions").textContent = m.insufficient_evidence_questions;
      document.getElementById("metric-answer-rate").textContent = `${m.answer_rate_percent}%`;

      // Render Machine Distribution Table
      const machineTbody = document.getElementById("supervisor-machine-stats-body");
      if (machineTbody && data.by_machine) {
        if (data.by_machine.length === 0) {
          machineTbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No machine queries logged yet.</td></tr>`;
        } else {
          machineTbody.innerHTML = data.by_machine.map(item => `
            <tr>
              <td><strong>${item.machine__machine_code}</strong></td>
              <td>${item.machine__machine_name}</td>
              <td><span class="badge bg-primary">${item.total}</span></td>
              <td>
                <span class="badge badge-answered me-1">${item.answered} Answered</span>
                <span class="badge badge-insufficient">${item.insufficient} Insufficient</span>
              </td>
            </tr>
          `).join("");
        }
      }
    } catch (err) {
      console.error("Failed to load metrics:", err);
    }
  }

  async function loadUnansweredQuestions() {
    const tbody = document.getElementById("supervisor-unanswered-body");
    if (!tbody) return;

    try {
      const resp = await App.apiFetch("/api/supervisor/unanswered/");
      if (!resp || !resp.ok) return;
      const data = await resp.json();

      if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No insufficient evidence or unanswered queries logged.</td></tr>`;
        return;
      }

      tbody.innerHTML = data.map(item => `
        <tr>
          <td><small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small></td>
          <td><span class="badge bg-secondary">${item.username}</span></td>
          <td><strong>${item.machine_code}</strong></td>
          <td><div class="fw-medium text-dark">${item.question}</div></td>
          <td><span class="badge badge-insufficient">${item.status}</span></td>
        </tr>
      `).join("");
    } catch (err) {
      console.error("Failed to load unanswered queries:", err);
    }
  }

  loadSupervisorMetrics();
  loadUnansweredQuestions();
});

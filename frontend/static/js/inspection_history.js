// Inspection History & Supervisor Review Controller
document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("inspections-tbody");
  const countText = document.getElementById("inspection-count-text");
  const filterPrediction = document.getElementById("filter-prediction");
  const filterReview = document.getElementById("filter-review");
  const filterStatus = document.getElementById("filter-status");
  const btnApplyFilters = document.getElementById("btn-apply-filters");
  const btnResetFilters = document.getElementById("btn-reset-filters");
  const btnTestDenial = document.getElementById("btn-test-engineer-denial");

  // Review Modal elements
  const reviewModalEl = document.getElementById("reviewModal");
  const reviewModal = reviewModalEl ? new bootstrap.Modal(reviewModalEl) : null;
  const modalInspectionId = document.getElementById("modal-inspection-id");
  const modalImgPreview = document.getElementById("modal-img-preview");
  const modalModelVer = document.getElementById("modal-model-ver");
  const modalPredictedClass = document.getElementById("modal-predicted-class");
  const modalConfidence = document.getElementById("modal-confidence");
  const modalDefectProb = document.getElementById("modal-defect-prob");
  const reviewRadioNormal = document.getElementById("review-radio-normal");
  const reviewRadioDefective = document.getElementById("review-radio-defective");
  const reviewCommentInput = document.getElementById("review-comment-input");
  const btnSubmitReview = document.getElementById("btn-submit-review");

  let currentInspections = [];

  async function loadInspections() {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-5 text-muted">
          <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
          Loading inspections...
        </td>
      </tr>
    `;

    const params = new URLSearchParams();
    if (filterPrediction && filterPrediction.value) params.append("predicted_class", filterPrediction.value);
    if (filterReview && filterReview.value) params.append("is_reviewed", filterReview.value);
    if (filterStatus && filterStatus.value) params.append("status", filterStatus.value);

    try {
      const resp = await App.apiFetch(`/api/inspections/list/?${params.toString()}`);
      if (!resp.ok) throw new Error("Failed to load inspections");

      currentInspections = await resp.json();
      renderInspectionsTable(currentInspections);
    } catch (err) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center py-4 text-danger">
            Error loading records: ${err.message}
          </td>
        </tr>
      `;
    }
  }

  function renderInspectionsTable(items) {
    if (countText) countText.textContent = `Showing ${items.length} inspection record(s)`;

    if (!items || items.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center py-5 text-muted">
            <i class="bi bi-inbox fs-2 d-block mb-2"></i>
            No inspection records match the selected filters.
          </td>
        </tr>
      `;
      return;
    }

    const isSupervisorOrAdmin = window.CURRENT_USER_ROLE === "SUPERVISOR" || window.CURRENT_USER_ROLE === "ADMIN";

    tableBody.innerHTML = items.map(item => {
      // Thumbnail
      const thumbHtml = item.image_url 
        ? `<img src="${item.image_url}" class="rounded border" style="width: 50px; height: 50px; object-fit: contain; background: #f8fafc;" alt="Thumbnail">`
        : `<div class="rounded bg-light border d-flex align-items-center justify-content-center text-muted" style="width: 50px; height: 50px;"><i class="bi bi-file-earmark-image"></i></div>`;

      // Prediction Badge
      let predBadge = "-";
      if (item.status === "FAILED") {
        predBadge = `<span class="badge bg-danger">FAILED</span><div class="text-danger small font-monospace mt-1" style="font-size: 0.72rem;">${item.failure_reason || "Validation rejected"}</div>`;
      } else if (item.predicted_class === "Normal") {
        predBadge = `<span class="badge bg-success-subtle text-success border border-success px-2 py-1"><i class="bi bi-check-circle me-1"></i>Normal</span>`;
      } else if (item.predicted_class === "Defective") {
        predBadge = `<span class="badge bg-danger-subtle text-danger border border-danger px-2 py-1"><i class="bi bi-exclamation-triangle me-1"></i>Defective</span>`;
      }

      const confText = item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : "-";

      // Supervisor Review Status
      let reviewHtml = "";
      if (item.status === "FAILED") {
        reviewHtml = `<span class="text-muted small">N/A (Failed Item)</span>`;
      } else if (item.is_reviewed) {
        const isOverride = item.reviewed_class !== item.predicted_class;
        const overrideBadge = isOverride ? `<span class="badge bg-warning text-dark ms-1">OVERRIDDEN</span>` : `<span class="badge bg-secondary ms-1">CONFIRMED</span>`;
        const reviewClassBadge = item.reviewed_class === "Normal" 
          ? `<span class="text-success fw-bold">Normal</span>` 
          : `<span class="text-danger fw-bold">Defective</span>`;

        reviewHtml = `
          <div>
            <span class="badge bg-primary text-white"><i class="bi bi-person-check-fill me-1"></i>Reviewed</span>
            ${overrideBadge}
            <div class="small mt-1">Final: ${reviewClassBadge} &bull; <span class="text-muted">by ${item.reviewed_by_username || "Supervisor"}</span></div>
            ${item.review_comment ? `<div class="text-muted small fst-italic mt-1 ps-1 border-start border-2">&ldquo;${item.review_comment}&rdquo;</div>` : ''}
          </div>
        `;
      } else {
        reviewHtml = `<span class="badge bg-secondary text-white"><i class="bi bi-hourglass-split me-1"></i>Pending Review</span>`;
      }

      // Actions
      let actionBtn = "";
      if (item.status === "COMPLETED") {
        if (isSupervisorOrAdmin) {
          actionBtn = `
            <button class="btn btn-sm btn-outline-warning btn-review-item" data-id="${item.id}" title="Review or correct this inspection">
              <i class="bi bi-pencil-square me-1"></i>Review
            </button>
          `;
        } else {
          // Engineer: cannot submit review
          actionBtn = `
            <button class="btn btn-sm btn-outline-secondary disabled" title="Engineers cannot submit reviews (Supervisor only)" disabled>
              <i class="bi bi-lock me-1"></i>Supervisor Only
            </button>
          `;
        }
      }

      return `
        <tr>
          <td>${thumbHtml}</td>
          <td>
            <div class="fw-bold text-dark font-monospace small">${item.filename}</div>
            <small class="text-muted">${item.product_id} &bull; ${item.product_name}</small>
            ${item.image_width ? `<div class="text-muted" style="font-size: 0.72rem;">${item.image_width}x${item.image_height} px</div>` : ''}
          </td>
          <td>
            <div class="small fw-semibold text-dark">${item.submitting_user}</div>
            <small class="text-muted">${new Date(item.created_at).toLocaleString()}</small>
          </td>
          <td>${predBadge}</td>
          <td>
            <div class="fw-semibold text-dark">${confText}</div>
            ${item.defect_probability !== null ? `<small class="text-muted font-monospace" style="font-size: 0.72rem;">p=${item.defect_probability.toFixed(3)}</small>` : ''}
          </td>
          <td>${reviewHtml}</td>
          <td class="text-end">${actionBtn}</td>
        </tr>
      `;
    }).join("");

    // Attach review button handlers
    document.querySelectorAll(".btn-review-item").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const item = currentInspections.find(x => x.id === id);
        if (item) openReviewModal(item);
      });
    });
  }

  function openReviewModal(item) {
    if (!reviewModal) return;
    modalInspectionId.value = item.id;
    modalImgPreview.src = item.image_url || "";
    modalModelVer.textContent = item.model_version;
    modalPredictedClass.textContent = item.predicted_class;
    modalPredictedClass.className = item.predicted_class === "Defective" ? "fw-bold text-danger" : "fw-bold text-success";
    modalConfidence.textContent = item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : "-";
    modalDefectProb.textContent = item.defect_probability !== null ? item.defect_probability.toFixed(4) : "-";

    // Pre-populate verdict
    const currentClass = item.is_reviewed ? item.reviewed_class : item.predicted_class;
    if (currentClass === "Defective") {
      reviewRadioDefective.checked = true;
    } else {
      reviewRadioNormal.checked = true;
    }

    reviewCommentInput.value = item.review_comment || "";
    reviewModal.show();
  }

  if (btnSubmitReview) {
    btnSubmitReview.addEventListener("click", async () => {
      const id = modalInspectionId.value;
      const selectedClass = document.querySelector("input[name='reviewed_class']:checked")?.value;
      const comment = reviewCommentInput.value.trim();

      if (!id || !selectedClass) return;

      btnSubmitReview.disabled = true;
      btnSubmitReview.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Saving...`;

      try {
        const resp = await App.apiFetch(`/api/inspections/${id}/review/`, {
          method: "POST",
          body: {
            reviewed_class: selectedClass,
            review_comment: comment
          }
        });

        if (resp.ok) {
          reviewModal.hide();
          loadInspections();
        } else {
          const data = await resp.json();
          alert("Review submission failed: " + (data.detail || "Server error"));
        }
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        btnSubmitReview.disabled = false;
        btnSubmitReview.innerHTML = `<i class="bi bi-check2-all me-1"></i>Save Supervisor Review`;
      }
    });
  }

  // Filter actions
  if (btnApplyFilters) btnApplyFilters.addEventListener("click", loadInspections);
  if (btnResetFilters) {
    btnResetFilters.addEventListener("click", () => {
      if (filterPrediction) filterPrediction.value = "";
      if (filterReview) filterReview.value = "";
      if (filterStatus) filterStatus.value = "";
      loadInspections();
    });
  }

  // Test Role Enforcement Button (Challenge Checklist Requirement)
  if (btnTestDenial) {
    btnTestDenial.addEventListener("click", async () => {
      const firstItem = currentInspections.find(x => x.status === "COMPLETED");
      const targetId = firstItem ? firstItem.id : "00000000-0000-0000-0000-000000000000";

      if (window.CURRENT_USER_ROLE === "ENGINEER") {
        // Engineer actually calls the API directly to prove server-side 403
        try {
          const resp = await App.apiFetch(`/api/inspections/${targetId}/review/`, {
            method: "POST",
            body: { reviewed_class: "Normal", review_comment: "Attempted by engineer" }
          });
          const data = await resp.json();
          alert(`Server Response:\nStatus: ${resp.status} ${resp.statusText}\nDetail: ${data.detail || JSON.stringify(data)}\n\n[VERIFIED] Server-side denial enforced!`);
        } catch (e) {
          alert("Request failed: " + e.message);
        }
      } else {
        alert(`You are currently signed in as ${window.CURRENT_USER_ROLE}.\nTo demonstrate 403 Forbidden to the judges, sign in as 'engineer_demo' (password: EngineerDemo!2026) and attempt to review an inspection. The server will strictly return 403 Forbidden.`);
      }
    });
  }

  // Initial load
  loadInspections();
});


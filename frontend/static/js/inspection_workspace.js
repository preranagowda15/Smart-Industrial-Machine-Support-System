// AI Visual Quality Inspection Workspace Controller
document.addEventListener("DOMContentLoaded", () => {
  // Single Inspection Elements
  const singleForm = document.getElementById("single-inspection-form");
  const singleProductSelect = document.getElementById("single-product-select");
  const singleDropzone = document.getElementById("single-dropzone");
  const singleFileInput = document.getElementById("single-file-input");
  const singlePreviewBox = document.getElementById("single-preview-box");
  const singlePreviewImg = document.getElementById("single-preview-img");
  const singleFileInfo = document.getElementById("single-file-info");
  const singleSubmitBtn = document.getElementById("single-submit-btn");

  const singleResultPlaceholder = document.getElementById("single-result-placeholder");
  const singleResultCard = document.getElementById("single-result-card");
  const resultInspectionId = document.getElementById("result-inspection-id");
  const resultTimestamp = document.getElementById("result-timestamp");
  const resultErrorAlert = document.getElementById("result-error-alert");
  const resultErrorMessage = document.getElementById("result-error-message");
  const resultSuccessContent = document.getElementById("result-success-content");
  const resultImagePreview = document.getElementById("result-image-preview");
  const resultImageMeta = document.getElementById("result-image-meta");
  const resultClassBadge = document.getElementById("result-class-badge");
  const resultConfidenceText = document.getElementById("result-confidence-text");
  const resultConfidenceBar = document.getElementById("result-confidence-bar");
  const resultDefectProb = document.getElementById("result-defect-prob");
  const resultProductMeta = document.getElementById("result-product-meta");
  const resultModelVersion = document.getElementById("result-model-version");
  const resultSubmittingUser = document.getElementById("result-submitting-user");

  let currentSingleFile = null;

  // Drag and Drop support
  if (singleDropzone) {
    singleDropzone.addEventListener("click", () => singleFileInput.click());
    singleDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      singleDropzone.classList.add("border-primary", "bg-white");
    });
    singleDropzone.addEventListener("dragleave", () => {
      singleDropzone.classList.remove("border-primary", "bg-white");
    });
    singleDropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      singleDropzone.classList.remove("border-primary", "bg-white");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });
  }

  if (singleFileInput) {
    singleFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  function handleFileSelect(file) {
    currentSingleFile = file;
    singlePreviewBox.classList.remove("d-none");
    singleFileInfo.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

    const reader = new FileReader();
    reader.onload = (e) => {
      singlePreviewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);

    singleSubmitBtn.disabled = false;
  }

  // Quick Demo Samples
  document.querySelectorAll(".demo-sample-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const url = btn.dataset.url;
      const filename = btn.dataset.name;
      try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error("Could not load sample file.");
        const blob = await resp.blob();
        const file = new File([blob], filename, { type: blob.type || "image/png" });
        handleFileSelect(file);
      } catch (err) {
        alert("Demo file loading error: " + err.message);
      }
    });
  });

  // Single Form Submit
  if (singleForm) {
    singleForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!currentSingleFile) return;

      const formData = new FormData();
      formData.append("product_id", singleProductSelect.value);
      formData.append("image", currentSingleFile);

      singleSubmitBtn.disabled = true;
      singleSubmitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        <span>Running BIT-PLATE-CV-1.0 Inference...</span>
      `;

      try {
        const resp = await App.apiFetch("/api/inspections/single/", {
          method: "POST",
          body: formData
        });

        singleResultPlaceholder.classList.add("d-none");
        singleResultCard.classList.remove("d-none");

        const data = await resp.json();

        if (resp.ok) {
          // Success
          resultErrorAlert.classList.add("d-none");
          resultSuccessContent.classList.remove("d-none");

          resultInspectionId.textContent = data.id;
          resultTimestamp.textContent = new Date(data.created_at).toLocaleString();

          resultImagePreview.src = data.image_url || singlePreviewImg.src;
          resultImageMeta.textContent = `${data.filename} • ${data.image_width}x${data.image_height} px • ${(data.file_size_bytes / 1024).toFixed(1)} KB`;

          const isDefective = data.predicted_class === "Defective";
          if (isDefective) {
            resultClassBadge.className = "badge bg-danger fs-4 px-3 py-2";
            resultClassBadge.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>DEFECTIVE`;
            resultConfidenceBar.className = "progress-bar bg-danger";
          } else {
            resultClassBadge.className = "badge bg-success fs-4 px-3 py-2";
            resultClassBadge.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>NORMAL`;
            resultConfidenceBar.className = "progress-bar bg-success";
          }

          const confPct = (data.confidence * 100).toFixed(1);
          resultConfidenceText.textContent = `${confPct}%`;
          resultConfidenceBar.style.width = `${confPct}%`;

          resultDefectProb.textContent = data.defect_probability !== null 
            ? data.defect_probability.toFixed(4) 
            : "-";

          resultProductMeta.textContent = `${data.product_id} - ${data.product_name}`;
          resultModelVersion.textContent = data.model_version;
          resultSubmittingUser.textContent = `${data.submitting_user} (${data.submitting_role})`;

        } else {
          // Validation error / rejection
          resultSuccessContent.classList.add("d-none");
          resultErrorAlert.classList.remove("d-none");

          resultInspectionId.textContent = data.inspection ? data.inspection.id : "REJECTED";
          resultTimestamp.textContent = new Date().toLocaleString();
          resultErrorMessage.textContent = data.detail || "Image validation rejected.";
        }
      } catch (err) {
        alert("Inspection error: " + err.message);
      } finally {
        singleSubmitBtn.disabled = false;
        singleSubmitBtn.innerHTML = `
          <i class="bi bi-search"></i>
          <span>Run AI Visual Inspection</span>
        `;
      }
    });
  }

  // ================= BATCH INSPECTION CONTROLLER =================
  const batchForm = document.getElementById("batch-inspection-form");
  const batchProductSelect = document.getElementById("batch-product-select");
  const batchFilesInput = document.getElementById("batch-files-input");
  const batchSelectedCount = document.getElementById("batch-selected-count");
  const batchFileCountText = document.getElementById("batch-file-count-text");
  const batchSubmitBtn = document.getElementById("batch-submit-btn");

  const batchStatusMeta = document.getElementById("batch-status-meta");
  const batchOverallBadge = document.getElementById("batch-overall-badge");
  const batchProgressLabel = document.getElementById("batch-progress-label");
  const batchProgressPercent = document.getElementById("batch-progress-percent");
  const batchProgressBar = document.getElementById("batch-progress-bar");
  const batchItemsTbody = document.getElementById("batch-items-tbody");

  let activePollInterval = null;

  if (batchFilesInput) {
    batchFilesInput.addEventListener("change", (e) => {
      const files = e.target.files;
      if (!files || files.length === 0) {
        batchSelectedCount.classList.add("d-none");
        batchSubmitBtn.disabled = true;
        return;
      }

      if (files.length > 10) {
        alert(`You selected ${files.length} files. Maximum allowed batch size is 10 files.`);
        batchFilesInput.value = "";
        batchSelectedCount.classList.add("d-none");
        batchSubmitBtn.disabled = true;
        return;
      }

      batchSelectedCount.classList.remove("d-none");
      batchFileCountText.textContent = `${files.length} file(s) selected for batch execution`;
      batchSubmitBtn.disabled = false;
    });
  }

  if (batchForm) {
    batchForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const files = batchFilesInput.files;
      if (!files || files.length === 0) return;

      const formData = new FormData();
      formData.append("product_id", batchProductSelect.value);
      for (let i = 0; i < files.length; i++) {
        formData.append("images", files[i]);
      }

      batchSubmitBtn.disabled = true;
      batchSubmitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        <span>Queueing Batch...</span>
      `;

      try {
        const resp = await App.apiFetch("/api/inspections/batch/", {
          method: "POST",
          body: formData
        });

        const data = await resp.json();
        if (resp.ok) {
          startBatchPolling(data.id);
        } else {
          alert("Batch queueing failed: " + (data.detail || "Unknown error"));
          batchSubmitBtn.disabled = false;
          batchSubmitBtn.innerHTML = `<i class="bi bi-play-circle-fill"></i><span>Queue &amp; Process Batch</span>`;
        }
      } catch (err) {
        alert("Batch error: " + err.message);
        batchSubmitBtn.disabled = false;
        batchSubmitBtn.innerHTML = `<i class="bi bi-play-circle-fill"></i><span>Queue &amp; Process Batch</span>`;
      }
    });
  }

  function startBatchPolling(batchId) {
    if (activePollInterval) clearInterval(activePollInterval);

    batchStatusMeta.textContent = `Batch ID: ${batchId} (Polling active...)`;
    pollBatchStatus(batchId);
    activePollInterval = setInterval(() => {
      pollBatchStatus(batchId);
    }, 1000);
  }

  async function pollBatchStatus(batchId) {
    try {
      const resp = await App.apiFetch(`/api/inspections/batch/${batchId}/status/`);
      if (!resp.ok) return;

      const batch = await resp.json();
      renderBatchStatus(batch);

      if (batch.status === "COMPLETED" || batch.status === "PARTIAL_FAILURE" || batch.status === "FAILED") {
        clearInterval(activePollInterval);
        activePollInterval = null;
        batchSubmitBtn.disabled = false;
        batchSubmitBtn.innerHTML = `<i class="bi bi-play-circle-fill"></i><span>Queue &amp; Process Batch</span>`;
      }
    } catch (e) {
      console.error("Batch poll error:", e);
    }
  }

  function renderBatchStatus(batch) {
    // Overall Badge
    const badgeColors = {
      QUEUED: "bg-secondary",
      PROCESSING: "bg-warning text-dark",
      COMPLETED: "bg-success",
      PARTIAL_FAILURE: "bg-warning text-dark",
      FAILED: "bg-danger"
    };
    batchOverallBadge.className = `badge ${badgeColors[batch.status] || "bg-secondary"}`;
    batchOverallBadge.textContent = batch.status;

    // Progress bar
    const done = batch.completed_items + batch.failed_items;
    const total = batch.total_items || 1;
    const pct = Math.round((done / total) * 100);

    batchProgressLabel.textContent = `Batch Progress: ${done} / ${batch.total_items} items finished`;
    batchProgressPercent.textContent = `${pct}%`;
    batchProgressBar.style.width = `${pct}%`;

    // Items table
    if (!batch.items || batch.items.length === 0) {
      batchItemsTbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No items in this batch.</td></tr>`;
      return;
    }

    batchItemsTbody.innerHTML = batch.items.map(item => {
      let itemStatusBadge = "";
      if (item.status === "COMPLETED") {
        itemStatusBadge = `<span class="badge bg-success">COMPLETED</span>`;
      } else if (item.status === "PROCESSING") {
        itemStatusBadge = `<span class="badge bg-warning text-dark"><span class="spinner-border spinner-border-sm me-1"></span>PROCESSING</span>`;
      } else if (item.status === "FAILED") {
        itemStatusBadge = `<span class="badge bg-danger">FAILED</span>`;
      } else {
        itemStatusBadge = `<span class="badge bg-secondary">QUEUED</span>`;
      }

      let predBadge = "-";
      if (item.predicted_class === "Normal") {
        predBadge = `<span class="badge bg-success-subtle text-success border border-success">Normal</span>`;
      } else if (item.predicted_class === "Defective") {
        predBadge = `<span class="badge bg-danger-subtle text-danger border border-danger">Defective</span>`;
      }

      const confText = item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : "-";
      const defectProbText = item.defect_probability !== null ? item.defect_probability.toFixed(4) : "-";
      const remarks = item.failure_reason 
        ? `<span class="text-danger small font-monospace">${item.failure_reason}</span>` 
        : (item.status === "COMPLETED" ? `<span class="text-success small"><i class="bi bi-check me-1"></i>Inference OK</span>` : "-");

      return `
        <tr>
          <td class="font-monospace small fw-bold">${item.filename}</td>
          <td>${itemStatusBadge}</td>
          <td>${predBadge}</td>
          <td>${confText}</td>
          <td class="font-monospace small">${defectProbText}</td>
          <td>${remarks}</td>
        </tr>
      `;
    }).join("");
  }
});


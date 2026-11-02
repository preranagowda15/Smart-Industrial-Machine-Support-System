// Manuals Management & Administrator Upload Controller
document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("manual-upload-form");
  const uploadBtn = document.getElementById("manual-upload-btn");
  const uploadStatusAlert = document.getElementById("upload-status-alert");

  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(uploadForm);

      uploadBtn.disabled = true;
      uploadBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Uploading & Indexing...`;
      if (uploadStatusAlert) uploadStatusAlert.classList.add("d-none");

      try {
        const resp = await App.apiFetch("/api/manuals/upload/", {
          method: "POST",
          body: formData
        });

        if (!resp) return;
        const data = await resp.json();

        if (resp.ok) {
          App.showToast("Manual successfully uploaded, extracted, and indexed!", "success");
          setTimeout(() => window.location.reload(), 1200);
        } else {
          if (uploadStatusAlert) {
            uploadStatusAlert.className = "alert alert-danger";
            uploadStatusAlert.textContent = data.detail || "Upload failed.";
            uploadStatusAlert.classList.remove("d-none");
          }
          App.showToast(data.detail || "Upload denied or failed.", "danger");
        }
      } catch (err) {
        if (uploadStatusAlert) {
          uploadStatusAlert.className = "alert alert-danger";
          uploadStatusAlert.textContent = err.message;
          uploadStatusAlert.classList.remove("d-none");
        }
      } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="bi bi-cloud-arrow-up-fill me-1"></i>Upload & Index Manual`;
      }
    });
  }
});


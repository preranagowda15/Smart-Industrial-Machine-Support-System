// AI Assistant Interface Controller
document.addEventListener("DOMContentLoaded", () => {
  const machineSelect = document.getElementById("assistant-machine-select");
  const chatMessages = document.getElementById("chat-messages");
  const questionInput = document.getElementById("assistant-question-input");
  const sendBtn = document.getElementById("assistant-send-btn");
  const chipsContainer = document.getElementById("prompt-chips-container");

  if (!chatMessages) return;

  const PROMPT_CHIPS = {
    "M-HP200": [
      "What does E17 mean?",
      "What should be inspected during maintenance, and what operating limits should be checked?",
      "What observations should be collected for repeated low hydraulic pressure?",
      "What is the maximum operating pressure?",
      "How often do I replace the hydraulic oil filter?",
      "What is the AC-90 rated discharge pressure?",
      "What is the pump replacement price from the supplier?"
    ],
    "M-AC90": [
      "What is the rated discharge pressure?",
      "What does alarm H03 mean?",
      "How often is the air intake filter replaced?",
      "What is the opening pressure of the safety relief valve?",
      "What does E17 mean on this compressor?",
      "How do I program the CNC lathe?"
    ]
  };

  function updateChips() {
    if (!chipsContainer || !machineSelect) return;
    const mid = machineSelect.value;
    const chips = PROMPT_CHIPS[mid] || [];
    chipsContainer.innerHTML = chips
      .map(q => `<button type="button" class="chip-btn">${q}</button>`)
      .join("");

    chipsContainer.querySelectorAll(".chip-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        questionInput.value = btn.textContent;
        submitQuestion();
      });
    });
  }

  if (machineSelect) {
    machineSelect.addEventListener("change", () => {
      updateChips();
      addSystemMessage(`Switched active machine to <strong>${machineSelect.options[machineSelect.selectedIndex].text}</strong>. Retrieval is strictly isolated to its manuals.`);
    });
    updateChips();
  }

  // Preselect machine or query from URL parameters if redirected from dashboard
  const urlParams = new URLSearchParams(window.location.search);
  const paramMachine = urlParams.get('machine');
  const paramQ = urlParams.get('q');
  if (paramMachine && machineSelect) {
    machineSelect.value = paramMachine;
    updateChips();
  }
  if (paramQ && questionInput) {
    questionInput.value = paramQ;
    setTimeout(() => {
      submitQuestion();
    }, 400);
  }

  function addSystemMessage(html) {
    const el = document.createElement("div");
    el.className = "text-center my-2 text-muted small";
    el.innerHTML = `<span class="badge bg-light text-dark border">${html}</span>`;
    chatMessages.appendChild(el);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function addUserMessage(text) {
    const el = document.createElement("div");
    el.className = "message-bubble message-user";
    el.textContent = text;
    chatMessages.appendChild(el);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function addLoadingIndicator() {
    const el = document.createElement("div");
    el.id = "chat-loading";
    el.className = "message-bubble message-assistant";
    el.innerHTML = `
      <div class="d-flex align-items-center gap-2 text-muted">
        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
        <span>Searching machine manual vector index and generating answer...</span>
      </div>
    `;
    chatMessages.appendChild(el);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return el;
  }

  function formatAnswerParagraphs(text) {
    if (!text) return "";
    // Replace double newlines with paragraphs, single newlines with <br>
    const paras = text.split(/\n\s*\n/);
    return paras.map(p => {
      const formatted = p.trim().replace(/\n/g, "<br>");
      return `<p class="mb-2">${formatted}</p>`;
    }).join("");
  }

  function renderAssistantResponse(data) {
    const loading = document.getElementById("chat-loading");
    if (loading) loading.remove();

    const isAnswered = data.status === "ANSWERED";
    const statusClass = isAnswered ? "message-answered" : "message-insufficient";
    const badgeHtml = isAnswered
      ? `<span class="badge bg-success px-2 py-1"><i class="bi bi-check-circle-fill me-1"></i>GROUNDED ANSWER FOUND</span>`
      : `<span class="badge bg-warning text-dark px-2 py-1"><i class="bi bi-exclamation-triangle-fill me-1"></i>INSUFFICIENT EVIDENCE</span>`;

    // Citations & Line Numbers HTML
    let citationsHtml = "";
    if (data.source_references && data.source_references.length > 0) {
      citationsHtml = `
        <div class="mt-3 pt-2 border-top">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <small class="text-secondary fw-bold text-uppercase" style="font-size: 0.75rem;">
              <i class="bi bi-journal-bookmark-fill text-primary me-1"></i>Verified Manual Sources & Citations:
            </small>
          </div>
          <div class="d-flex flex-column gap-2">
            ${data.source_references.map(src => {
              const hasLinePrefix = src.passage_text && src.passage_text.startsWith("[Lines ");
              const lineRange = hasLinePrefix 
                ? src.passage_text.slice(1, src.passage_text.indexOf(']')) 
                : '';
              const cleanPassage = hasLinePrefix 
                ? src.passage_text.slice(src.passage_text.indexOf(']\n') + 2) 
                : (src.passage_text || '');

              const lineBadge = lineRange 
                ? `<span class="badge bg-primary text-white"><i class="bi bi-list-ol me-1"></i>${lineRange}</span>` 
                : '';

              return `
                <div class="citation-card p-2 bg-light rounded border">
                  <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-1">
                    <div class="d-flex align-items-center gap-2">
                      <strong class="text-dark"><i class="bi bi-file-earmark-pdf text-danger me-1"></i>${src.document_name}</strong> 
                      <span class="badge bg-secondary">Rev ${src.revision}</span>
                      <span class="badge bg-dark">PDF Page ${src.pdf_page}</span>
                      ${lineBadge}
                    </div>
                    <a href="${src.pdf_url}" target="_blank" class="btn btn-sm btn-outline-primary py-0 px-2" title="Open PDF Page">
                      <i class="bi bi-box-arrow-up-right me-1"></i>Open PDF Page
                    </a>
                  </div>
                  <details class="mt-2 text-muted small">
                    <summary class="cursor-pointer text-primary" style="font-size: 0.8rem; cursor: pointer;">
                      <i class="bi bi-chevron-right me-1"></i>Click to view verbatim manual passage (${lineRange || 'Page ' + src.pdf_page})
                    </summary>
                    <div class="passage-text p-2 mt-1 bg-white rounded border border-secondary border-opacity-25 fst-italic">
                      "${cleanPassage}"
                    </div>
                  </details>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }

    const formattedAnswer = formatAnswerParagraphs(data.answer);

    const el = document.createElement("div");
    el.className = `message-bubble message-assistant ${statusClass} shadow-sm`;
    el.innerHTML = `
      <div class="d-flex align-items-center justify-content-between mb-2">
        <div class="d-flex align-items-center gap-2">
          ${badgeHtml}
          <span class="badge bg-light text-dark border">
            <i class="bi bi-cpu me-1 text-primary"></i>${data.machine_code || machineSelect.value}
          </span>
        </div>
        <small class="text-muted">${new Date().toLocaleTimeString()}</small>
      </div>
      
      <!-- Primary Highlighted Answer Card -->
      <div class="p-3 my-2 rounded-3 bg-white border border-primary border-opacity-50 shadow-sm" style="background-color: #f8fafc !important;">
        <div class="d-flex align-items-center justify-content-between mb-2 pb-1 border-bottom">
          <div class="d-flex align-items-center gap-2 text-primary fw-bold" style="font-size: 0.85rem;">
            <i class="bi bi-robot fs-5"></i>
            <span class="text-uppercase tracking-wider">AI Assistant Answer (from Official Manuals):</span>
          </div>
          ${data.source_references && data.source_references.length > 0 ? `
            <span class="badge bg-info text-dark" style="font-size: 0.72rem;">
              <i class="bi bi-check2-all me-1"></i>Grounded & Verified
            </span>
          ` : ''}
        </div>
        
        <!-- Answer Body in Paragraph Form -->
        <div class="text-dark lh-base" style="font-size: 1rem; color: #0f172a !important;">
          ${formattedAnswer}
        </div>
      </div>

      <!-- Verified Citations & Line Numbers -->
      ${citationsHtml}
    `;

    chatMessages.appendChild(el);

    // Scroll to position the answer at the top of the chat area
    setTimeout(() => {
      chatMessages.scrollTo({
        top: el.offsetTop - 15,
        behavior: "smooth"
      });
    }, 50);
  }

  async function submitQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    const mid = machineSelect.value;
    addUserMessage(question);
    questionInput.value = "";
    sendBtn.disabled = true;
    const loadingEl = addLoadingIndicator();

    try {
      const resp = await App.apiFetch("/api/assistant/ask/", {
        method: "POST",
        body: {
          machine_id: mid,
          question: question
        }
      });

      if (!resp) return;
      const data = await resp.json();
      if (resp.ok) {
        renderAssistantResponse(data);
      } else {
        loadingEl.remove();
        addSystemMessage(`<span class="text-danger">Error: ${data.detail || "Request failed"}</span>`);
      }
    } catch (err) {
      loadingEl.remove();
      addSystemMessage(`<span class="text-danger">Request error: ${err.message}</span>`);
    } finally {
      sendBtn.disabled = false;
      questionInput.focus();
    }
  }

  if (sendBtn) {
    sendBtn.addEventListener("click", submitQuestion);
  }

  if (questionInput) {
    questionInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitQuestion();
      }
    });
  }
});

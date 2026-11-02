// Citation & PDF Navigation Controller
document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a[href*='#page=']");
    if (!link) return;
    // Highlight cited passage if clicked in page
    const card = link.closest(".citation-card");
    if (card) {
      card.classList.add("border-primary");
      setTimeout(() => card.classList.remove("border-primary"), 1500);
    }
  });
});


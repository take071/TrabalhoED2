// Scripts complementares da aplicação GlobalSIM
document.addEventListener("DOMContentLoaded", () => {
  // Inicialização de tooltips do Bootstrap caso existam
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

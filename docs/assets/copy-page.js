document.addEventListener("click", async (event) => {
  const button = event.target.closest(".extras-copy-page");
  if (!button) return;

  const tools = button.closest(".extras-page-tools");
  const status = tools.querySelector(".extras-copy-status");
  const source = tools.nextElementSibling;
  if (!source || source.id !== "extras-page-markdown") return;

  try {
    await navigator.clipboard.writeText(JSON.parse(source.textContent));
    status.textContent = "Markdown copied";
  } catch {
    status.textContent = "Could not copy. Check clipboard permissions.";
  }
});

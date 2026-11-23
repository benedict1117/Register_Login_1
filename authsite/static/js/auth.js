// Show / hide password
document.querySelectorAll("[data-toggle-password]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = btn.parentElement.querySelector("input");
    const show = input.type === "password";
    input.type = show ? "text" : "password";
    btn.setAttribute("aria-pressed", String(show));
    btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
    input.focus();
  });
});

// Back button: go to the previous page when there is one, else follow the link.
document.querySelectorAll("[data-back]").forEach((link) => {
  link.addEventListener("click", (event) => {
    if (window.history.length > 1 && document.referrer) {
      event.preventDefault();
      window.history.back();
    }
  });
});

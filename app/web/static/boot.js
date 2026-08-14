(() => {
  const path = (location.pathname || "/").replace(/\/+$/, "") || "/";
  let layout = "landing";
  if (path === "/login") layout = "login";
  else if (["/passwort", "/sprache", "/onboarding", "/datenschutz"].includes(path)) layout = "auth";
  else if (path.startsWith("/ausbilder")) layout = "trainer";
  else if (path.startsWith("/admin")) layout = "admin";
  else if (path !== "/" && path !== "/funktionen") layout = "app";
  document.body.dataset.pageLayout = layout;
  if (layout === "login" || layout === "auth" || layout === "app" || layout === "landing") {
    const stored = localStorage.getItem("ol_theme") || "light";
    if (stored === "system") {
      document.documentElement.dataset.theme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    } else {
      document.documentElement.dataset.theme = stored;
    }
    document.documentElement.classList.toggle("high-contrast", localStorage.getItem("ol_high_contrast") === "1");
    document.documentElement.classList.toggle("reduce-motion", localStorage.getItem("ol_reduce_motion") === "1");
  }
})();

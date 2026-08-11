const state = {
  chapter: null,
  questions: [],
  exams: [],
  journey: [],
  dashboard: null,
  currentQuestionIndex: 0,
  activeExam: null,
  accessToken: localStorage.getItem("ol_access_token"),
  learnerId: localStorage.getItem("ol_learner_id"),
};

const routeConfig = {
  "/": { layout: "landing", title: "BZE Online Campus" },
  "/funktionen": { layout: "landing", title: "Features" },
  "/login": { layout: "login", title: "Login" },
  "/dashboard": { layout: "app", view: "dashboard", title: "Dashboard" },
  "/lernreise": { layout: "app", view: "journey", title: "Lernreise" },
  "/lernen": { layout: "app", view: "learn", title: "Kapitel 1: Einstieg" },
  "/pruefungen": { layout: "app", view: "exam", title: "Testpruefungen" },
  "/defizite": { layout: "app", view: "progress", title: "Defizite" },
  "/review": { layout: "app", view: "admin", title: "Review" },
  "/datenschutz": { layout: "app", view: "privacy", title: "Datenschutz" },
};

const viewRoutes = Object.fromEntries(
  Object.entries(routeConfig)
    .filter(([, config]) => config.view)
    .map(([path, config]) => [config.view, path]),
);

function authHeaders() {
  return state.accessToken ? { Authorization: `Bearer ${state.accessToken}` } : {};
}

function clearSession() {
  state.accessToken = null;
  state.learnerId = null;
  localStorage.removeItem("ol_access_token");
  localStorage.removeItem("ol_learner_id");
  document.body.classList.remove("is-authenticated");
}

function getRouteConfig(pathname = window.location.pathname) {
  return routeConfig[pathname] || routeConfig["/"];
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `API Fehler: ${response.status}`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function login(identifier, password, cohortCode) {
  const session = await fetchJson("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      identifier,
      password,
      cohort_code: cohortCode || null,
    }),
  });
  state.accessToken = session.access_token;
  state.learnerId = session.learner_id;
  localStorage.setItem("ol_access_token", session.access_token);
  localStorage.setItem("ol_learner_id", session.learner_id);
  document.body.classList.add("is-authenticated");
  await refreshPrivateData();
}

async function ensureDemoSession() {
  if (state.accessToken) {
    document.body.classList.add("is-authenticated");
    try {
      await refreshPrivateData();
      return;
    } catch (error) {
      clearSession();
    }
  }
  await login("demo-azubi", "demo-pass", "BZE-2026-F");
}

async function refreshPrivateData() {
  state.dashboard = await fetchJson("/api/dashboard", { headers: authHeaders() });
  state.journey = await fetchJson("/api/learning/journey", { headers: authHeaders() });
  renderDashboard();
  renderStats();
  renderJourney();
}

async function navigateTo(pathname, pushState = true) {
  const config = getRouteConfig(pathname);
  if (pushState && window.location.pathname !== pathname) {
    window.history.pushState({}, "", pathname);
  }
  document.body.dataset.pageLayout = config.layout;
  document.title = `${config.title} | BZE Online Campus`;
  if (config.layout === "app") {
    await ensureDemoSession();
    switchView(config.view, false);
  }
  if (config.layout === "login") {
    document.title = "Login | BZE Online Campus";
  }
}

function switchView(viewName, updateRoute = true) {
  document.querySelectorAll(".nav-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `${viewName}-view`);
  });
  const titleMap = {
    dashboard: "Dashboard",
    journey: "Lernreise",
    learn: "Kapitel 1: Einstieg",
    exam: "Testpruefungen",
    progress: "Defizite",
    admin: "Review",
    privacy: "Datenschutz",
  };
  document.getElementById("page-title").textContent = titleMap[viewName];
  if (updateRoute && viewRoutes[viewName]) {
    window.history.pushState({}, "", viewRoutes[viewName]);
    document.title = `${titleMap[viewName]} | BZE Online Campus`;
  }
  if (viewName === "progress") {
    renderProgress();
  }
}

function renderStats() {
  const dashboard = state.dashboard || {
    mastered_questions: 0,
    wrong_answers: 0,
  };
  document.getElementById("mastered-count").textContent =
    dashboard.mastered_questions;
  document.getElementById("wrong-count").textContent = dashboard.wrong_answers;
}

function renderDashboard() {
  if (!state.dashboard) {
    return;
  }
  document.getElementById("dashboard-level").textContent = state.dashboard.level;
  document.getElementById("dashboard-xp").textContent = state.dashboard.xp;
  document.getElementById("dashboard-mastered").textContent =
    state.dashboard.mastered_questions;
  document.getElementById("dashboard-open").textContent =
    state.dashboard.total_questions - state.dashboard.mastered_questions;
  document.getElementById("dashboard-rule").textContent =
    state.dashboard.mastery_rule;
  document.getElementById("weak-list").innerHTML =
    state.dashboard.weak_categories.length === 0
      ? "<li>Noch keine Defizite erkannt.</li>"
      : state.dashboard.weak_categories
          .map(
            (item) =>
              `<li><strong>${item.category_slug}</strong><span>${item.wrong_count} Fehler</span></li>`,
          )
          .join("");
}

function renderJourney() {
  const markup = state.journey
    .map(
      (month) => `
        <button class="journey-node ${month.checkpoint ? "checkpoint" : ""} ${
          month.locked ? "locked" : ""
        }">
          <strong>M${String(month.month).padStart(2, "0")}</strong>
          <span>${month.title}</span>
          <small>${month.completed_categories}/${month.total_categories}</small>
        </button>
      `,
    )
    .join("");
  document.getElementById("journey-map").innerHTML = markup;
  document.getElementById("journey-map-full").innerHTML = markup;
}

function renderChapter() {
  document.getElementById("chapter-title").textContent = state.chapter.title;
  document.getElementById("chapter-goal").textContent =
    state.chapter.mission_goal;
  document.getElementById("lesson-copy").innerHTML = state.chapter.fachkunde
    .map((paragraph) => `<p>${paragraph}</p>`)
    .join("");
  document.getElementById("subchapter-list").innerHTML = state.chapter.subchapters
    .map(
      (category) => `
        <div class="subchapter-item">
          <strong>${category.subchapter_number}. ${category.title}</strong>
          <span>${String(category.month).padStart(2, "0")}</span>
        </div>
      `,
    )
    .join("");
}

function renderQuestion() {
  const question = state.questions[state.currentQuestionIndex % state.questions.length];
  document.getElementById("question-category").textContent = question.category_slug;
  document.getElementById("question-state").textContent = "Backend Tracking";
  document.getElementById("question-prompt").textContent = question.prompt;
  document.getElementById("answer-feedback").textContent = "";
  document.getElementById("answer-options").innerHTML = question.options
    .map(
      (option, index) => `
        <button class="answer-option" data-index="${index}">
          ${index + 1}. ${option}
        </button>
      `,
    )
    .join("");
}

async function answerQuestion(index) {
  await ensureDemoSession();
  const question = state.questions[state.currentQuestionIndex % state.questions.length];
  const result = await fetchJson("/api/progress/attempt", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      question_id: question.question_id,
      selected_option_index: index,
    }),
  });
  document.querySelectorAll(".answer-option").forEach((button) => {
    const optionIndex = Number(button.dataset.index);
    button.disabled = true;
    if (optionIndex === result.correct_option_index) {
      button.classList.add("correct");
    }
    if (optionIndex === index && !result.is_correct) {
      button.classList.add("wrong");
    }
  });
  document.getElementById("question-state").textContent =
    `${result.correct_streak}/2 richtig`;
  document.getElementById("answer-feedback").textContent = result.explanation;
  await refreshPrivateData();
}

function renderExamSelect() {
  const select = document.getElementById("exam-select");
  select.innerHTML = state.exams
    .map((exam) => `<option value="${exam.exam_id}">${exam.title}</option>`)
    .join("");
  state.activeExam = state.exams[0];
  renderExam();
}

function renderExam() {
  const exam = state.activeExam;
  document.getElementById("exam-panel").innerHTML = `
    <h3>${exam.title}</h3>
    <p>${exam.description}</p>
    <ol class="exam-list">
      ${exam.questions
        .map(
          (question) => `
            <li>
              <strong>${question.prompt}</strong>
              <div>${question.options
                .map((option, index) => `${index + 1}. ${option}`)
                .join("<br>")}</div>
            </li>
          `,
        )
        .join("")}
    </ol>
  `;
}

function renderProgress() {
  if (!state.dashboard) {
    return;
  }
  document.getElementById("progress-grid").innerHTML = [
    ["Offene Fragen", state.dashboard.total_questions - state.dashboard.mastered_questions],
    ["Fragen mit Fehlern", state.dashboard.wrong_answers],
    ["Regel", state.dashboard.mastery_rule],
  ]
    .map(
      ([label, value]) => `
      <div class="progress-item">
        <strong>${value}</strong>
        <span>${label}</span>
      </div>`,
    )
    .join("");
}

async function generateDraft() {
  const draft = await fetchJson("/api/content/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      occupation_slug: "maschinen-und-anlagenfuehrer",
      specialization_slug: "metall-und-kunststofftechnik",
      month: 8,
      learner_level: "azubi",
    }),
  });
  document.getElementById("draft-output").innerHTML = `
    <h3>${draft.title}</h3>
    <p><strong>Lernziel:</strong> ${draft.learning_goal}</p>
    <p>${draft.fachkunde}</p>
    <p><strong>Status:</strong> ${draft.review_status}</p>
    <p><strong>Quellen:</strong> ${draft.source_keys.join(", ")}</p>
  `;
}

async function resetProgress() {
  await ensureDemoSession();
  await fetchJson("/api/progress/reset", {
    method: "POST",
    headers: authHeaders(),
  });
  await refreshPrivateData();
  renderProgress();
  renderQuestion();
}

function setPrivacyFeedback(message) {
  document.getElementById("privacy-feedback").textContent = message;
}

async function acceptPrivacyNotice() {
  await ensureDemoSession();
  await fetchJson("/api/privacy/consent", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ accepted: true }),
  });
  setPrivacyFeedback("Datenschutzbestaetigung gespeichert.");
}

async function exportLearnerData() {
  await ensureDemoSession();
  const exportPayload = await fetchJson("/api/privacy/export", {
    headers: authHeaders(),
  });
  const output = document.getElementById("draft-output");
  output.replaceChildren();
  const title = document.createElement("h3");
  const description = document.createElement("p");
  const pre = document.createElement("pre");
  title.textContent = "Dein Datenexport";
  description.textContent =
    "Der Export enthaelt Profil, Lernstand, Einwilligungen und Kennzahlen.";
  pre.textContent = JSON.stringify(exportPayload.data, null, 2);
  output.append(title, description, pre);
  setPrivacyFeedback("Datenexport im Review-Bereich angezeigt.");
  switchView("admin");
}

async function logout() {
  if (state.accessToken) {
    await fetchJson("/api/auth/logout", {
      method: "POST",
      headers: authHeaders(),
    }).catch(() => null);
  }
  clearSession();
  setPrivacyFeedback("Abgemeldet. Demo-Zugang kann jederzeit neu gestartet werden.");
}

async function deleteAccount() {
  await ensureDemoSession();
  const confirmed = window.confirm(
    "Lernkonto wirklich loeschen? Fortschritt, Sessions und Einwilligungen werden entfernt.",
  );
  if (!confirmed) {
    setPrivacyFeedback("Loeschung abgebrochen.");
    return;
  }
  await fetchJson("/api/privacy/account", {
    method: "DELETE",
    headers: authHeaders(),
  });
  clearSession();
  setPrivacyFeedback("Lernkonto geloescht. Demo-Zugang kann neu angelegt werden.");
  await ensureDemoSession();
  renderProgress();
}

async function init() {
  state.chapter = await fetchJson("/api/learning/first-chapter");
  state.questions = await fetchJson("/api/questions?month=1");
  state.exams = await fetchJson("/api/exams");
  if (state.accessToken) {
    try {
      await refreshPrivateData();
    } catch (error) {
      clearSession();
    }
  }
  renderChapter();
  renderQuestion();
  renderExamSelect();
  await navigateTo(window.location.pathname, false);
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("a, button");
  if (!target) {
    return;
  }
  if (target.matches("[data-page-link]")) {
    event.preventDefault();
    await navigateTo(new URL(target.href).pathname);
    return;
  }
  if (target.matches(".answer-option")) {
    await answerQuestion(Number(target.dataset.index));
  }
  if (target.matches("[data-login-demo]")) {
    event.preventDefault();
    await login("demo-azubi", "demo-pass", "BZE-2026-F");
    await navigateTo("/dashboard");
  }
  if (target.dataset.privacyAction === "consent") {
    await acceptPrivacyNotice();
  }
  if (target.dataset.privacyAction === "export") {
    await exportLearnerData();
  }
  if (target.dataset.privacyAction === "logout") {
    await logout();
  }
  if (target.dataset.privacyAction === "delete") {
    await deleteAccount();
  }
});

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  await login(
    String(form.get("identifier")),
    String(form.get("password")),
    String(form.get("cohort")),
  );
  document.getElementById("login-feedback").textContent =
    "Angemeldet. Serverseitiger Lernstand ist aktiv.";
  await navigateTo("/dashboard");
});

document.getElementById("next-question").addEventListener("click", () => {
  state.currentQuestionIndex += 1;
  renderQuestion();
});

document.getElementById("exam-select").addEventListener("change", (event) => {
  state.activeExam = state.exams.find((exam) => exam.exam_id === event.target.value);
  renderExam();
});

document.getElementById("reset-progress").addEventListener("click", resetProgress);
document.getElementById("generate-draft").addEventListener("click", generateDraft);
document.getElementById("accept-privacy").addEventListener("click", acceptPrivacyNotice);
document.getElementById("export-data").addEventListener("click", exportLearnerData);
document.getElementById("logout").addEventListener("click", logout);
document.getElementById("delete-account").addEventListener("click", deleteAccount);

window.addEventListener("popstate", async () => {
  await navigateTo(window.location.pathname, false);
});

init().catch((error) => {
  document.body.replaceChildren();
  const errorBox = document.createElement("pre");
  errorBox.textContent = error.message;
  document.body.append(errorBox);
});

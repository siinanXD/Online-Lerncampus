const state = {
  chapter: null,
  questions: [],
  units: [],
  activeUnit: null,
  learnMonth: 1,
  exams: [],
  journey: [],
  dashboard: null,
  trainingReports: [],
  currentQuestionIndex: 0,
  activeExam: null,
  examSession: null,
  examChoiceAnswers: {},
  examOpenAnswers: {},
  examResult: null,
  examTimerHandle: null,
  accessToken: localStorage.getItem("ol_access_token"),
  learnerId: localStorage.getItem("ol_learner_id"),
  currentPath: "/",
};

const routeConfig = window.OLC_ROUTE_CONFIG || {};

function resolveRoute(pathname = window.location.pathname) {
  let config = routeConfig[pathname];
  let guard = 0;
  while (config?.aliasOf && guard < 5) {
    pathname = config.aliasOf;
    config = routeConfig[pathname];
    guard += 1;
  }
  return { pathname, config: config || routeConfig["/"] || { layout: "landing", title: "BZE" } };
}

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

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) {
    return;
  }
  toast.hidden = false;
  toast.textContent = message;
  window.clearTimeout(showToast._timer);
  showToast._timer = window.setTimeout(() => {
    toast.hidden = true;
  }, 2400);
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

async function ensureAuthenticated() {
  document.body.classList.add("is-authenticated");
  await refreshPrivateData();
}

async function requireAuth() {
  if (!state.accessToken) {
    await navigateTo("/login");
    throw new Error("Anmeldung erforderlich.");
  }
  await ensureAuthenticated();
}

async function refreshPrivateData() {
  state.dashboard = await fetchJson("/api/dashboard", { headers: authHeaders() });
  state.journey = await fetchJson("/api/learning/journey", { headers: authHeaders() });
  state.trainingReports = await fetchJson("/api/training-reports", {
    headers: authHeaders(),
  }).catch(() => []);
  renderStats();
}

function mountRoot(layout) {
  if (layout === "auth") {
    return document.getElementById("auth-root");
  }
  if (layout === "trainer") {
    return document.getElementById("trainer-root");
  }
  if (layout === "admin") {
    return document.getElementById("admin-root");
  }
  return document.getElementById("screen-root");
}

function renderScreen(config) {
  const layout = config.layout || "app";
  const root = mountRoot(layout);
  if (!root) {
    return;
  }
  if (layout === "landing" || layout === "login") {
    root.innerHTML = "";
    return;
  }
  const renderer = window.OLC_SCREEN_RENDERERS?.[config.screen];
  root.innerHTML = renderer ? renderer() : `<article class="card"><p>Screen fehlt: ${config.screen || "?"}</p></article>`;
  bindLiveData(root, config);
}

function bindLiveData(root, config) {
  const dashboard = state.dashboard;
  const mastered = dashboard?.mastered_questions || 0;
  const wrong = dashboard?.wrong_answers || 0;
  const total = dashboard?.total_questions || 0;
  const readiness = total ? Math.round((mastered / total) * 100) : 0;

  root.querySelectorAll("[data-bind='mastered']").forEach((el) => {
    el.textContent = String(mastered);
  });
  root.querySelectorAll("[data-bind='wrong']").forEach((el) => {
    el.textContent = String(wrong);
  });
  root.querySelectorAll("[data-bind='readiness']").forEach((el) => {
    el.textContent = `${readiness}%`;
  });
  root.querySelectorAll("[data-bind='profile-summary']").forEach((el) => {
    el.textContent = state.accessToken
      ? `Angemeldet als ${state.learnerId || "Azubi"}.`
      : "Nicht angemeldet.";
  });

  const questionList = root.querySelector("[data-bind='question-list']");
  if (questionList) {
    const source =
      config.path === "/lernen/fragen/fehler" || config.screen?.includes("fehler")
        ? state.questions.slice(0, 8)
        : state.questions.slice(0, 12);
    questionList.innerHTML = source.length
      ? source
          .map(
            (question, index) => `
          <a class="list-row" href="/lernen/frage" data-page-link data-q-index="${index}">
            <strong>${index + 1}. ${question.prompt}</strong>
            <span class="muted">${question.category_slug || "Frage"}</span>
          </a>`,
          )
          .join("")
      : `<article class="list-row"><strong>Keine Fragen geladen</strong><span class="muted">Demo</span></article>`;
  }

  const livePrompt = root.querySelector("[data-bind='live-question-prompt']");
  const liveAnswers = root.querySelector("[data-bind='live-answers']");
  if (livePrompt && state.questions.length) {
    const question = state.questions[state.currentQuestionIndex % state.questions.length];
    livePrompt.textContent = question.prompt;
    if (liveAnswers) {
      liveAnswers.innerHTML = question.options
        .map(
          (option, index) => `
          <button class="answer-option" type="button" data-index="${index}">
            ${index + 1}. ${option}
          </button>`,
        )
        .join("");
    }
  }

  const examLive = root.querySelector("[data-bind='exam-live']");
  if (examLive) {
    renderExamInto(examLive);
  }

  const reportsLive = root.querySelector("[data-bind='reports-live']");
  if (reportsLive) {
    reportsLive.innerHTML = renderReportsMarkup();
  }

  const levelRing = document.querySelector("#level-pill .level-ring");
  if (levelRing) {
    levelRing.textContent = String(Math.max(1, Math.min(99, Math.floor(mastered / 20) + 1)));
  }
}

function renderStats() {
  const dashboard = state.dashboard || { mastered_questions: 0, wrong_answers: 0 };
  const stats = document.getElementById("app-stats");
  if (!stats) {
    return;
  }
  stats.innerHTML = `
    <span class="stat-chip">${dashboard.mastered_questions} gemeistert</span>
    <span class="stat-chip">${dashboard.wrong_answers} Fehler</span>
  `;
}

function renderReportsMarkup() {
  return `
    <div class="report-list">
      ${
        state.trainingReports
          .map(
            (report) => `
          <article class="report-card card">
            <header>
              <strong>${report.report_date}</strong>
              <span>${report.hours} h · ${report.status}</span>
            </header>
            <p>${report.activities}</p>
          </article>`,
          )
          .join("") ||
        `<article class="card"><p class="muted">Noch keine Berichtsheft-Eintraege.</p>
          <a class="primary-button" href="/berichtsheft/neu" data-page-link>Ersten Eintrag schreiben</a></article>`
      }
    </div>`;
}

function clearExamTimer() {
  if (state.examTimerHandle) {
    window.clearInterval(state.examTimerHandle);
    state.examTimerHandle = null;
  }
}

function resetExamAttempt() {
  clearExamTimer();
  state.examSession = null;
  state.examChoiceAnswers = {};
  state.examOpenAnswers = {};
  state.examResult = null;
}

function formatExamTimer(expiresAt) {
  if (!expiresAt) {
    return "Ohne Zeitlimit";
  }
  const remainingMs = new Date(expiresAt).getTime() - Date.now();
  if (remainingMs <= 0) {
    return "Zeit abgelaufen";
  }
  const totalSeconds = Math.floor(remainingMs / 1000);
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function startExamTimer(root) {
  clearExamTimer();
  if (!state.examSession?.expires_at) {
    return;
  }
  const timerElement = root.querySelector("#exam-timer");
  if (!timerElement) {
    return;
  }
  const tick = () => {
    timerElement.textContent = formatExamTimer(state.examSession.expires_at);
  };
  tick();
  state.examTimerHandle = window.setInterval(tick, 1000);
}

function renderExamInto(target) {
  if (!state.exams.length) {
    target.innerHTML = `<p class="muted">Keine Pruefungen geladen.</p>`;
    return;
  }
  if (!state.activeExam) {
    state.activeExam = state.exams[0];
  }
  if (state.examResult) {
    const result = state.examResult;
    target.innerHTML = `
      <div class="exam-result card">
        <h3>Ergebnis: ${result.passed ? "Bestanden" : "Nicht bestanden"}</h3>
        <p><strong>${result.score_percent}%</strong> (${result.choice_correct}/${result.choice_total} SC richtig)</p>
        <p>Bestehensgrenze: ${result.passing_score_percent}%</p>
        <div class="row-actions">
          <button id="exam-restart" class="primary-button" type="button">Neue Session</button>
          <a class="secondary-button" href="/pruefungen/schwach" data-page-link>Schwache Themen</a>
        </div>
      </div>`;
    return;
  }
  if (state.examSession) {
    const exam = state.examSession.exam;
    const choiceMarkup = exam.questions
      .map((question, index) => {
        const selected = state.examChoiceAnswers[question.question_id];
        return `
          <li class="exam-question">
            <strong>${index + 1}. ${question.prompt}</strong>
            <div class="answer-options">
              ${question.options
                .map(
                  (option, optionIndex) => `
                    <button type="button" class="exam-answer-option ${
                      selected === optionIndex ? "selected" : ""
                    }" data-exam-action="choice" data-question-id="${question.question_id}" data-index="${optionIndex}">
                      ${optionIndex + 1}. ${option}
                    </button>`,
                )
                .join("")}
            </div>
          </li>`;
      })
      .join("");
    target.innerHTML = `
      <div class="exam-session card">
        <div class="exam-session-header">
          <div><h3>${exam.title}</h3><p>${exam.description}</p></div>
          <div class="exam-session-meta">
            <span id="exam-timer">${formatExamTimer(state.examSession.expires_at)}</span>
            <span>Bestehen: ${state.examSession.passing_score_percent}%</span>
          </div>
        </div>
        <ol class="exam-list">${choiceMarkup}</ol>
        <div class="exam-actions">
          <button id="exam-submit" class="primary-button" type="button">Pruefung abgeben</button>
          <button id="exam-cancel" class="secondary-button" type="button">Abbrechen</button>
        </div>
        <p id="exam-feedback" class="feedback"></p>
      </div>`;
    startExamTimer(target);
    return;
  }

  const options = state.exams
    .map(
      (exam) =>
        `<option value="${exam.exam_id}" ${
          exam.exam_id === state.activeExam.exam_id ? "selected" : ""
        }>${exam.title}</option>`,
    )
    .join("");
  const exam = state.activeExam;
  target.innerHTML = `
    <label class="field"><span>Pruefung</span><select id="exam-select">${options}</select></label>
    <div class="exam-preview card">
      <h3>${exam.title}</h3>
      <p>${exam.description}</p>
      <p>${exam.questions.length} Single-Choice-Fragen${
        exam.open_questions?.length ? `, ${exam.open_questions.length} offene Aufgaben` : ""
      }${exam.time_limit_minutes ? `, Zeitlimit ${exam.time_limit_minutes} Minuten` : ", ohne Zeitlimit"}.</p>
      <button id="exam-start" class="primary-button" type="button">Pruefung starten</button>
      <p id="exam-feedback" class="feedback"></p>
    </div>`;
}

async function startExamSession() {
  await requireAuth();
  resetExamAttempt();
  const payload = await fetchJson(`/api/exams/${state.activeExam.exam_id}/sessions`, {
    method: "POST",
    headers: authHeaders(),
  });
  state.examSession = payload;
  await navigateTo("/pruefungen", false);
}

async function saveExamChoiceAnswer(questionId, optionIndex) {
  if (!state.examSession) {
    return;
  }
  await fetchJson(`/api/exams/sessions/${state.examSession.session_id}/answers`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      selected_option_index: optionIndex,
    }),
  });
  state.examChoiceAnswers[questionId] = optionIndex;
  await navigateTo("/pruefungen", false);
}

async function submitExamSession() {
  if (!state.examSession) {
    return;
  }
  clearExamTimer();
  state.examResult = await fetchJson(
    `/api/exams/sessions/${state.examSession.session_id}/submit`,
    { method: "POST", headers: authHeaders() },
  );
  state.examSession = null;
  await navigateTo(state.examResult.passed ? "/pruefungen/bestanden" : "/pruefungen/durchgefallen");
}

async function answerQuestion(index) {
  await requireAuth();
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
  const feedback = document.querySelector("[data-bind='live-feedback']");
  if (feedback) {
    feedback.textContent = result.explanation;
  }
  await refreshPrivateData();
  showToast(result.is_correct ? "Richtig! +XP" : "Leider falsch");
}

async function saveTrainingReport(formElement) {
  await requireAuth();
  const form = new FormData(formElement);
  await fetchJson("/api/training-reports", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      report_date: String(form.get("report_date")),
      activities: String(form.get("activities")),
      hours: Number(form.get("hours")),
    }),
  });
  await refreshPrivateData();
  showToast("Berichtsheft-Eintrag gespeichert");
  await navigateTo("/berichtsheft");
}

async function changePassword(formElement) {
  await requireAuth();
  const form = new FormData(formElement);
  const next = String(form.get("next"));
  const confirm = String(form.get("confirm"));
  if (next !== confirm) {
    throw new Error("Passwoerter stimmen nicht ueberein.");
  }
  await fetchJson("/api/auth/password", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      current_password: String(form.get("current")),
      new_password: next,
      repeated_password: confirm,
    }),
  });
  showToast("Passwort gespeichert");
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
  const output = document.querySelector("[data-bind='trainer-output']");
  if (output) {
    output.innerHTML = `
      <h3>${draft.title}</h3>
      <p><strong>Lernziel:</strong> ${draft.learning_goal}</p>
      <p>${draft.fachkunde}</p>
      <p><strong>Status:</strong> ${draft.review_status}</p>`;
  }
}

async function loadReviews() {
  await requireAuth();
  const rows = await fetchJson("/api/content/review/pending", { headers: authHeaders() }).catch(
    () => [],
  );
  const output = document.querySelector("[data-bind='trainer-output']");
  if (!output) {
    return;
  }
  output.innerHTML = rows.length
    ? `<ul class="plain-list">${rows
        .map((row) => `<li>${row.entity_type}: ${row.entity_key} · ${row.status}</li>`)
        .join("")}</ul>`
    : `<p class="muted">Keine offenen Reviews (oder keine Berechtigung).</p>`;
}

async function exportLearnerData() {
  await requireAuth();
  const exportPayload = await fetchJson("/api/privacy/export", { headers: authHeaders() });
  const pre = document.querySelector("[data-bind='export-pre']");
  if (pre) {
    pre.hidden = false;
    pre.textContent = JSON.stringify(exportPayload.data, null, 2);
  }
  showToast("Datenexport geladen");
}

async function logout() {
  if (state.accessToken) {
    await fetchJson("/api/auth/logout", {
      method: "POST",
      headers: authHeaders(),
    }).catch(() => null);
  }
  clearSession();
  showToast("Abgemeldet");
  await navigateTo("/login");
}

async function deleteAccount() {
  await requireAuth();
  const confirmed = window.confirm(
    "Lernkonto wirklich loeschen? Fortschritt, Sessions und Einwilligungen werden entfernt.",
  );
  if (!confirmed) {
    return;
  }
  await fetchJson("/api/privacy/account", {
    method: "DELETE",
    headers: authHeaders(),
  });
  clearSession();
  showToast("Lernkonto geloescht");
  await navigateTo("/login");
}

function updateChrome(config, pathname) {
  document.body.dataset.pageLayout = config.layout || "landing";
  document.title = `${config.title || "BZE"} | BZE Online Campus`;
  const title = document.getElementById("page-title");
  const eyebrow = document.getElementById("page-eyebrow");
  if (title) {
    title.textContent = config.title || "App";
  }
  if (eyebrow) {
    eyebrow.textContent = config.num ? `${config.num}` : "Teilnehmer";
  }
  const tab = config.tab;
  document.querySelectorAll(".tab-bar a").forEach((link) => {
    const view = link.dataset.view;
    const active =
      (tab === "dashboard" && view === "dashboard") ||
      (tab === "learn" && view === "learn") ||
      (tab === "exam" && view === "exam") ||
      (tab === "reports" && view === "reports") ||
      (tab === "progress" && view === "profile" ? false : tab === "profile" && view === "profile") ||
      (pathname.startsWith("/fortschritt") && view === "profile" && false);
    const mapped =
      (tab === "dashboard" && view === "dashboard") ||
      (tab === "learn" && view === "learn") ||
      (tab === "exam" && view === "exam") ||
      (tab === "reports" && view === "reports") ||
      ((tab === "profile" || tab === "progress") && view === "profile");
    link.classList.toggle("active", Boolean(mapped));
  });
  document.querySelectorAll(".desk-nav a").forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === pathname);
  });
}

async function navigateTo(pathname, pushState = true) {
  const resolved = resolveRoute(pathname);
  const config = { ...resolved.config, path: resolved.pathname };
  if (pushState && window.location.pathname !== resolved.pathname) {
    window.history.pushState({}, "", resolved.pathname);
  } else if (pushState && pathname !== resolved.pathname && routeConfig[pathname]?.aliasOf) {
    window.history.replaceState({}, "", resolved.pathname);
  }
  state.currentPath = resolved.pathname;
  if (["app", "trainer", "admin"].includes(config.layout) && state.accessToken) {
    try {
      await ensureAuthenticated();
    } catch (error) {
      clearSession();
    }
  }
  updateChrome(config, resolved.pathname);
  renderScreen(config);
}

async function loadLearnMonth(month) {
  state.learnMonth = month;
  state.currentQuestionIndex = 0;
  const [units, questions, categories] = await Promise.all([
    fetchJson(`/api/learning/units?month=${month}`),
    fetchJson(`/api/questions?month=${month}`),
    fetchJson(`/api/questions/categories?month=${month}`),
  ]);
  state.units = units;
  state.questions = questions;
  state.chapter = {
    title: `Monat ${month}`,
    subchapters: categories,
  };
}

async function init() {
  state.chapter = await fetchJson("/api/learning/first-chapter");
  state.questions = await fetchJson("/api/questions?month=1");
  state.units = await fetchJson("/api/learning/units?month=1");
  state.exams = await fetchJson("/api/exams");
  state.activeExam = state.exams[0] || null;
  if (state.accessToken) {
    try {
      await refreshPrivateData();
    } catch (error) {
      clearSession();
    }
  }
  await navigateTo(window.location.pathname, false);
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("a, button");
  if (!target) {
    return;
  }
  try {
    if (target.matches("[data-page-link]")) {
      event.preventDefault();
      if (target.dataset.qIndex) {
        state.currentQuestionIndex = Number(target.dataset.qIndex);
      }
      await navigateTo(new URL(target.href, window.location.origin).pathname);
      return;
    }
    if (target.matches("[data-login-demo]")) {
      event.preventDefault();
      await login("demo-azubi", "demo-pass", "BZE-2026-F");
      await navigateTo("/dashboard");
      return;
    }
    if (target.dataset.action === "toast") {
      showToast(target.dataset.toast || "OK");
      return;
    }
    if (target.dataset.action === "logout") {
      await logout();
      return;
    }
    if (target.dataset.action === "delete-account") {
      await deleteAccount();
      return;
    }
    if (target.dataset.action === "export-data") {
      await exportLearnerData();
      return;
    }
    if (target.dataset.action === "generate-draft") {
      await generateDraft();
      return;
    }
    if (target.dataset.action === "load-reviews") {
      await loadReviews();
      return;
    }
    if (target.dataset.action === "exam-start-shortcut" || target.id === "exam-start") {
      event.preventDefault();
      await startExamSession();
      return;
    }
    if (target.id === "exam-submit") {
      await submitExamSession();
      return;
    }
    if (target.id === "exam-cancel" || target.id === "exam-restart") {
      resetExamAttempt();
      await navigateTo("/pruefungen", false);
      return;
    }
    if (target.matches(".exam-answer-option")) {
      await saveExamChoiceAnswer(target.dataset.questionId, Number(target.dataset.index));
      return;
    }
    if (target.matches(".answer-option") && target.dataset.index !== undefined) {
      await answerQuestion(Number(target.dataset.index));
      return;
    }
    if (target.matches(".lang-option")) {
      document.querySelectorAll(".lang-option").forEach((el) => el.classList.remove("active"));
      target.classList.add("active");
      showToast(`Sprache: ${target.textContent}`);
    }
  } catch (error) {
    showToast(error.message);
    const feedback = document.getElementById("exam-feedback");
    if (feedback) {
      feedback.textContent = error.message;
    }
  }
});

document.addEventListener("change", (event) => {
  if (event.target.id === "exam-select") {
    state.activeExam = state.exams.find((exam) => exam.exam_id === event.target.value);
    resetExamAttempt();
    navigateTo("/pruefungen", false);
  }
});

document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) {
    return;
  }
  try {
    if (form.id === "login-form") {
      event.preventDefault();
      const data = new FormData(form);
      await login(String(data.get("identifier")), String(data.get("password")), String(data.get("cohort")));
      document.getElementById("login-feedback").textContent =
        "Angemeldet. Serverseitiger Lernstand ist aktiv.";
      await navigateTo("/dashboard");
      return;
    }
    if (form.dataset.action === "change-password") {
      event.preventDefault();
      await changePassword(form);
      const feedback = form.parentElement.querySelector("[data-feedback]");
      if (feedback) {
        feedback.textContent = "Passwort gespeichert.";
      }
      return;
    }
    if (form.dataset.action === "create-report") {
      event.preventDefault();
      await saveTrainingReport(form);
    }
  } catch (error) {
    showToast(error.message);
    const feedback = form.parentElement?.querySelector("[data-feedback]");
    if (feedback) {
      feedback.textContent = error.message;
    }
  }
});

window.addEventListener("popstate", async () => {
  await navigateTo(window.location.pathname, false);
});

init().catch((error) => {
  document.body.replaceChildren();
  const errorBox = document.createElement("pre");
  errorBox.textContent = error.message;
  document.body.append(errorBox);
});

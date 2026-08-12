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
};

const routeConfig = {
  "/": { layout: "landing", title: "BZE Online Campus" },
  "/funktionen": { layout: "landing", title: "Features" },
  "/login": { layout: "login", title: "Login" },
  "/dashboard": { layout: "app", view: "dashboard", title: "Dashboard" },
  "/lernreise": { layout: "app", view: "journey", title: "Lernreise" },
  "/lernen": { layout: "app", view: "learn", title: "Kapitel 1: Einstieg" },
  "/pruefungen": { layout: "app", view: "exam", title: "Testpruefungen" },
  "/berichtsheft": { layout: "app", view: "reports", title: "Berichtsheft" },
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
    if (state.accessToken) {
      try {
        await ensureAuthenticated();
      } catch (error) {
        clearSession();
      }
    }
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
    reports: "Berichtsheft",
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
  if (viewName === "reports") {
    renderTrainingReports();
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
  document.getElementById("subchapter-list").innerHTML = state.chapter.subchapters
    .map(
      (category) => `
        <div class="subchapter-item">
          <strong>${category.subchapter_number}. ${category.title}</strong>
          <span>M${String(category.month).padStart(2, "0")}</span>
        </div>
      `,
    )
    .join("");
}

function renderUnitList() {
  const list = document.getElementById("unit-list");
  const detail = document.getElementById("unit-detail");
  if (state.activeUnit) {
    list.classList.add("hidden");
    detail.classList.remove("hidden");
    return;
  }
  list.classList.remove("hidden");
  detail.classList.add("hidden");
  list.innerHTML = state.units
    .map(
      (unit) => `
        <button class="unit-card" data-unit-slug="${unit.slug}">
          <strong>${unit.position}. ${unit.title}</strong>
          <span>${unit.subtitle}</span>
          <small>${unit.estimated_minutes} Min · ${unit.category_slugs[0]}</small>
        </button>
      `,
    )
    .join("");
}

function renderUnitDetail(unit) {
  document.getElementById("unit-title").textContent = unit.title;
  document.getElementById("unit-subtitle").textContent = unit.subtitle;
  document.getElementById("unit-goals").innerHTML = unit.learning_goals
    .map((goal) => `<li>${goal}</li>`)
    .join("");
  document.getElementById("unit-theory").innerHTML = unit.theory_blocks
    .map(
      (block) => `
        <article class="theory-block">
          <h4>${block.heading}</h4>
          <p>${block.body.replace(/\n\n/g, "</p><p>")}</p>
          <ul>${block.key_points.map((point) => `<li>${point}</li>`).join("")}</ul>
          ${
            block.norm_references.length
              ? `<p class="norm-ref">Normen: ${block.norm_references.join(", ")}</p>`
              : ""
          }
        </article>
      `,
    )
    .join("");
  document.getElementById("unit-glossary").innerHTML = Object.entries(unit.glossary)
    .map(([term, definition]) => `<dt>${term}</dt><dd>${definition}</dd>`)
    .join("");
  document.getElementById("unit-practice").textContent = unit.practice_task;
}

async function loadLearnMonth(month) {
  state.learnMonth = month;
  state.activeUnit = null;
  state.currentQuestionIndex = 0;
  const [chapter, units, questions] = await Promise.all([
    fetchJson(`/api/occupations/maschinen-und-anlagenfuehrer/curriculum`).then(
      (curriculum) => {
        const entry = curriculum.find((item) => item.month === month);
        return {
          title: `Monat ${month}: ${entry.title}`,
          mission_goal: entry.learning_goals.join(" "),
          subchapters: state.chapter?.subchapters?.length
            ? state.chapter.subchapters
            : [],
        };
      },
    ),
    fetchJson(`/api/learning/units?month=${month}`),
    fetchJson(`/api/questions?month=${month}`),
  ]);
  const categories = await fetchJson(`/api/questions/categories?month=${month}`);
  state.chapter = {
    ...chapter,
    subchapters: categories,
  };
  state.units = units;
  state.questions = questions;
  renderChapter();
  renderUnitList();
  renderQuestion();
  document.getElementById("page-title").textContent = `Monat ${month} | Lernen`;
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
  document.getElementById("question-state").textContent =
    `${result.correct_streak}/2 richtig`;
  document.getElementById("answer-feedback").textContent = result.explanation;
  await refreshPrivateData();
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

function startExamTimer() {
  clearExamTimer();
  if (!state.examSession?.expires_at) {
    return;
  }
  const timerElement = document.getElementById("exam-timer");
  if (!timerElement) {
    return;
  }
  const tick = () => {
    timerElement.textContent = formatExamTimer(state.examSession.expires_at);
  };
  tick();
  state.examTimerHandle = window.setInterval(tick, 1000);
}

function renderExamSelect() {
  const select = document.getElementById("exam-select");
  select.innerHTML = state.exams
    .map((exam) => `<option value="${exam.exam_id}">${exam.title}</option>`)
    .join("");
  state.activeExam = state.exams[0];
  resetExamAttempt();
  renderExam();
}

function renderExamResult() {
  const result = state.examResult;
  document.getElementById("exam-panel").innerHTML = `
    <div class="exam-result">
      <h3>Ergebnis: ${result.passed ? "Bestanden" : "Nicht bestanden"}</h3>
      <p><strong>${result.score_percent}%</strong> (${result.choice_correct}/${result.choice_total} SC richtig)</p>
      <p>Bestehensgrenze: ${result.passing_score_percent}%</p>
      ${
        result.open_max_points
          ? `<p>Offene Aufgaben: ${result.open_score}/${result.open_max_points} Punkte</p>`
          : ""
      }
      ${
        result.weak_categories.length
          ? `<div class="exam-weaknesses">
              <h4>Schwache Bereiche</h4>
              <ul>${result.weak_categories
                .map(
                  (item) =>
                    `<li>${item.category_slug}: ${item.wrong_count} Fehler</li>`,
                )
                .join("")}</ul>
            </div>`
          : "<p>Keine auffaelligen Schwaechen in den SC-Aufgaben.</p>"
      }
      <button id="exam-restart" class="primary-button">Neue Session starten</button>
    </div>
  `;
}

function renderExamSession() {
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
                  <button
                    type="button"
                    class="exam-answer-option ${
                      selected === optionIndex ? "selected" : ""
                    }"
                    data-exam-action="choice"
                    data-question-id="${question.question_id}"
                    data-index="${optionIndex}"
                  >
                    ${optionIndex + 1}. ${option}
                  </button>
                `,
              )
              .join("")}
          </div>
        </li>
      `;
    })
    .join("");

  const openMarkup = (exam.open_questions || [])
    .map((question, index) => {
      const saved = state.examOpenAnswers[question.question_id];
      return `
        <li class="exam-open-question">
          <strong>Offen ${index + 1}. ${question.prompt}</strong>
          <p>Max. ${question.max_points} Punkte</p>
          <textarea
            class="exam-open-input"
            data-question-id="${question.question_id}"
            rows="4"
            placeholder="Deine Antwort..."
          >${saved?.learner_answer || ""}</textarea>
          <label>
            Selbsteinschaetzung (0-${question.max_points})
            <input
              type="number"
              min="0"
              max="${question.max_points}"
              class="exam-open-score"
              data-question-id="${question.question_id}"
              value="${saved?.self_score ?? ""}"
            />
          </label>
          <button
            type="button"
            class="secondary-button"
            data-exam-action="open"
            data-question-id="${question.question_id}"
          >
            Offene Antwort speichern
          </button>
        </li>
      `;
    })
    .join("");

  document.getElementById("exam-panel").innerHTML = `
    <div class="exam-session">
      <div class="exam-session-header">
        <div>
          <h3>${exam.title}</h3>
          <p>${exam.description}</p>
        </div>
        <div class="exam-session-meta">
          <span id="exam-timer">${formatExamTimer(state.examSession.expires_at)}</span>
          <span>Bestehen: ${state.examSession.passing_score_percent}%</span>
        </div>
      </div>
      <ol class="exam-list">${choiceMarkup}</ol>
      ${
        openMarkup
          ? `<h4>Offene Aufgaben</h4><ol class="exam-open-list">${openMarkup}</ol>`
          : ""
      }
      <div class="exam-actions">
        <button id="exam-submit" class="primary-button">Pruefung abgeben</button>
        <button id="exam-cancel" class="secondary-button">Abbrechen</button>
      </div>
      <p id="exam-feedback" class="feedback"></p>
    </div>
  `;
  startExamTimer();
}

function renderExamPreview() {
  const exam = state.activeExam;
  document.getElementById("exam-panel").innerHTML = `
    <div class="exam-preview">
      <h3>${exam.title}</h3>
      <p>${exam.description}</p>
      <p>${exam.questions.length} Single-Choice-Fragen${
        exam.open_questions?.length
          ? `, ${exam.open_questions.length} offene Aufgaben`
          : ""
      }${
        exam.time_limit_minutes
          ? `, Zeitlimit ${exam.time_limit_minutes} Minuten`
          : ", ohne Zeitlimit"
      }.</p>
      <button id="exam-start" class="primary-button">Pruefung starten</button>
      <p id="exam-feedback" class="feedback"></p>
    </div>
  `;
}

function renderExam() {
  if (state.examResult) {
    renderExamResult();
    return;
  }
  if (state.examSession) {
    renderExamSession();
    return;
  }
  if (!state.activeExam) {
    return;
  }
  renderExamPreview();
}

async function startExamSession() {
  await requireAuth();
  resetExamAttempt();
  const payload = await fetchJson(`/api/exams/${state.activeExam.exam_id}/sessions`, {
    method: "POST",
    headers: authHeaders(),
  });
  state.examSession = payload;
  renderExam();
}

async function saveExamChoiceAnswer(questionId, optionIndex) {
  if (!state.examSession) {
    return;
  }
  await fetchJson(`/api/exams/sessions/${state.examSession.session_id}/answers`, {
    method: "POST",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question_id: questionId,
      selected_option_index: optionIndex,
    }),
  });
  state.examChoiceAnswers[questionId] = optionIndex;
  renderExamSession();
}

async function saveExamOpenAnswer(questionId) {
  if (!state.examSession) {
    return;
  }
  const answerInput = document.querySelector(
    `.exam-open-input[data-question-id="${questionId}"]`,
  );
  const scoreInput = document.querySelector(
    `.exam-open-score[data-question-id="${questionId}"]`,
  );
  const learnerAnswer = answerInput.value.trim();
  const selfScoreRaw = scoreInput.value.trim();
  const selfScore = selfScoreRaw === "" ? null : Number(selfScoreRaw);
  await fetchJson(
    `/api/exams/sessions/${state.examSession.session_id}/open-answers`,
    {
      method: "POST",
      headers: {
        ...authHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: questionId,
        learner_answer: learnerAnswer,
        self_score: selfScore,
      }),
    },
  );
  state.examOpenAnswers[questionId] = {
    learner_answer: learnerAnswer,
    self_score: selfScore,
  };
  document.getElementById("exam-feedback").textContent =
    "Offene Antwort gespeichert.";
}

async function submitExamSession() {
  if (!state.examSession) {
    return;
  }
  clearExamTimer();
  state.examResult = await fetchJson(
    `/api/exams/sessions/${state.examSession.session_id}/submit`,
    {
      method: "POST",
      headers: authHeaders(),
    },
  );
  state.examSession = null;
  renderExam();
}

function renderTrainingReports() {
  const panel = document.getElementById("reports-panel");
  if (!panel) {
    return;
  }
  panel.innerHTML = `
    <form id="report-form" class="report-form">
      <label>Datum<input type="date" name="report_date" required /></label>
      <label>Stunden<input type="number" name="hours" min="1" max="12" step="0.5" value="8" required /></label>
      <label>Taetigkeiten<textarea name="activities" rows="5" required placeholder="Was hast du heute gelernt und gemacht?"></textarea></label>
      <button type="submit" class="primary-button">Eintrag speichern</button>
    </form>
    <div class="report-list">
      ${state.trainingReports
        .map(
          (report) => `
            <article class="report-card">
              <header>
                <strong>${report.report_date}</strong>
                <span>${report.hours} h · ${report.status}</span>
              </header>
              <p>${report.activities}</p>
            </article>
          `,
        )
        .join("") || "<p>Noch keine Berichtsheft-Eintraege.</p>"}
    </div>
  `;
}

async function saveTrainingReport(event) {
  event.preventDefault();
  await requireAuth();
  const form = new FormData(event.currentTarget);
  await fetchJson("/api/training-reports", {
    method: "POST",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      report_date: String(form.get("report_date")),
      activities: String(form.get("activities")),
      hours: Number(form.get("hours")),
    }),
  });
  await refreshPrivateData();
  renderTrainingReports();
}

function cancelExamSession() {
  resetExamAttempt();
  renderExam();
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
  await requireAuth();
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
  await requireAuth();
  await fetchJson("/api/privacy/consent", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ accepted: true }),
  });
  setPrivacyFeedback("Datenschutzbestaetigung gespeichert.");
}

async function exportLearnerData() {
  await requireAuth();
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
  await requireAuth();
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
  setPrivacyFeedback("Lernkonto geloescht.");
  await navigateTo("/login");
  renderProgress();
}

async function init() {
  state.chapter = await fetchJson("/api/learning/first-chapter");
  state.questions = await fetchJson("/api/questions?month=1");
  state.units = await fetchJson("/api/learning/units?month=1");
  state.exams = await fetchJson("/api/exams");
  const monthSelect = document.getElementById("learn-month-select");
  monthSelect.innerHTML = Array.from({ length: 24 }, (_, index) => {
    const month = index + 1;
    return `<option value="${month}">Monat ${month}</option>`;
  }).join("");
  monthSelect.value = "1";
  if (state.accessToken) {
    try {
      await refreshPrivateData();
    } catch (error) {
      clearSession();
    }
  }
  renderChapter();
  renderUnitList();
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
  if (target.matches(".unit-card")) {
    const slug = target.dataset.unitSlug;
    state.activeUnit = state.units.find((unit) => unit.slug === slug);
    if (state.activeUnit) {
      renderUnitDetail(state.activeUnit);
      renderUnitList();
    }
    return;
  }
  if (target.id === "unit-back") {
    state.activeUnit = null;
    renderUnitList();
    return;
  }
  if (target.matches(".answer-option")) {
    await answerQuestion(Number(target.dataset.index));
  }
  if (target.id === "report-form" || target.closest("#report-form")) {
    return;
  }
  if (target.id === "exam-start") {
    try {
      await startExamSession();
    } catch (error) {
      document.getElementById("exam-feedback").textContent = error.message;
    }
  }
  if (target.id === "exam-submit") {
    try {
      await submitExamSession();
    } catch (error) {
      document.getElementById("exam-feedback").textContent = error.message;
    }
  }
  if (target.id === "exam-cancel" || target.id === "exam-restart") {
    cancelExamSession();
  }
  if (target.matches(".exam-answer-option")) {
    try {
      await saveExamChoiceAnswer(target.dataset.questionId, Number(target.dataset.index));
    } catch (error) {
      document.getElementById("exam-feedback").textContent = error.message;
    }
  }
  if (target.dataset.examAction === "open") {
    try {
      await saveExamOpenAnswer(target.dataset.questionId);
    } catch (error) {
      document.getElementById("exam-feedback").textContent = error.message;
    }
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

document.getElementById("learn-month-select").addEventListener("change", async (event) => {
  await loadLearnMonth(Number(event.target.value));
});

document.getElementById("next-question").addEventListener("click", () => {
  state.currentQuestionIndex += 1;
  renderQuestion();
});

document.getElementById("exam-select").addEventListener("change", (event) => {
  state.activeExam = state.exams.find((exam) => exam.exam_id === event.target.value);
  resetExamAttempt();
  renderExam();
});

document.getElementById("reset-progress").addEventListener("click", resetProgress);
document.getElementById("generate-draft").addEventListener("click", generateDraft);
document.getElementById("accept-privacy").addEventListener("click", acceptPrivacyNotice);
document.getElementById("export-data").addEventListener("click", exportLearnerData);
document.getElementById("logout").addEventListener("click", logout);
document.getElementById("delete-account").addEventListener("click", deleteAccount);
document.addEventListener("submit", async (event) => {
  if (event.target.id === "report-form") {
    event.preventDefault();
    await saveTrainingReport(event);
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

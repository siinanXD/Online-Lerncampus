const state = {
  chapter: null,
  questions: [],
  units: [],
  activeUnit: null,
  learnMonth: 1,
  exams: [],
  journey: [],
  dashboard: null,
  profile: null,
  gamification: null,
  coachPlan: null,
  pendingReviews: [],
  occupations: [],
  curriculum: [],
  sources: [],
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
  role: localStorage.getItem("ol_role") || "learner",
  displayName: localStorage.getItem("ol_display_name") || "",
  currentPath: "/",
};

const routeConfig = window.OLC_ROUTE_CONFIG || {};
const STAFF_ROLES = new Set(["reviewer", "trainer", "admin"]);

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
  state.role = "learner";
  state.displayName = "";
  state.profile = null;
  state.dashboard = null;
  state.gamification = null;
  state.coachPlan = null;
  state.pendingReviews = [];
  localStorage.removeItem("ol_access_token");
  localStorage.removeItem("ol_learner_id");
  localStorage.removeItem("ol_role");
  localStorage.removeItem("ol_display_name");
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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
          : `API Fehler: ${response.status}`;
    throw new Error(message);
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
  state.role = session.role || "learner";
  state.displayName = session.display_name || "";
  localStorage.setItem("ol_access_token", session.access_token);
  localStorage.setItem("ol_learner_id", session.learner_id);
  localStorage.setItem("ol_role", state.role);
  localStorage.setItem("ol_display_name", state.displayName);
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

function requireStaff() {
  if (!STAFF_ROLES.has(state.role)) {
    throw new Error("Nur fuer Reviewer, Trainer oder Admin.");
  }
}

async function refreshPrivateData() {
  state.profile = await fetchJson("/api/auth/me", { headers: authHeaders() });
  state.learnerId = state.profile.learner_id;
  state.role = state.profile.role || "learner";
  state.displayName = state.profile.display_name || "";
  localStorage.setItem("ol_learner_id", state.learnerId);
  localStorage.setItem("ol_role", state.role);
  localStorage.setItem("ol_display_name", state.displayName);
  state.dashboard = await fetchJson("/api/dashboard", { headers: authHeaders() });
  state.journey = await fetchJson("/api/learning/journey", { headers: authHeaders() });
  state.gamification = await fetchJson("/api/gamification", { headers: authHeaders() }).catch(
    () => null,
  );
  state.coachPlan = await fetchJson("/api/coach/plan", { headers: authHeaders() }).catch(() => null);
  state.trainingReports = await fetchJson("/api/training-reports", {
    headers: authHeaders(),
  }).catch(() => []);
  if (STAFF_ROLES.has(state.role)) {
    state.pendingReviews = await fetchJson("/api/content/review/pending", {
      headers: authHeaders(),
    }).catch(() => []);
  } else {
    state.pendingReviews = [];
  }
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
  root.innerHTML = renderer
    ? renderer()
    : `<article class="card"><p>Screen fehlt: ${config.screen || "?"}</p></article>`;
  bindLiveData(root, config);
}

function bindLiveData(root, config) {
  const dashboard = state.dashboard;
  const mastered = dashboard?.mastered_questions || 0;
  const wrong = dashboard?.wrong_answers || 0;
  const total = dashboard?.total_questions || 0;
  const readiness = total ? Math.round((mastered / total) * 100) : 0;
  const xp = dashboard?.xp ?? state.gamification?.xp ?? 0;
  const level = dashboard?.level ?? state.gamification?.level ?? 1;
  const streak = dashboard?.streak_days ?? state.gamification?.streak_days ?? 0;

  root.querySelectorAll("[data-bind='mastered']").forEach((el) => {
    el.textContent = String(mastered);
  });
  root.querySelectorAll("[data-bind='wrong']").forEach((el) => {
    el.textContent = String(wrong);
  });
  root.querySelectorAll("[data-bind='readiness']").forEach((el) => {
    el.textContent = `${readiness}%`;
  });
  root.querySelectorAll("[data-bind='xp']").forEach((el) => {
    el.textContent = String(xp);
  });
  root.querySelectorAll("[data-bind='level']").forEach((el) => {
    el.textContent = String(level);
  });
  root.querySelectorAll("[data-bind='streak']").forEach((el) => {
    el.textContent = String(streak);
  });
  root.querySelectorAll("[data-bind='profile-summary']").forEach((el) => {
    el.textContent = state.accessToken
      ? `${state.displayName || "Azubi"} · ${state.role} · ${state.learnerId || ""}`
      : "Nicht angemeldet.";
  });
  root.querySelectorAll("[data-bind='role']").forEach((el) => {
    el.textContent = state.role || "learner";
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
            <strong>${index + 1}. ${escapeHtml(question.prompt)}</strong>
            <span class="muted">${escapeHtml(question.category_slug || "Frage")}</span>
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
            ${index + 1}. ${escapeHtml(option)}
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

  const unitsLive = root.querySelector("[data-bind='units-live']");
  if (unitsLive) {
    unitsLive.innerHTML = renderUnitsMarkup();
  }

  const unitDetail = root.querySelector("[data-bind='unit-detail']");
  if (unitDetail) {
    unitDetail.innerHTML = renderUnitDetailMarkup();
  }

  const journeyLive = root.querySelector("[data-bind='journey-live']");
  if (journeyLive) {
    journeyLive.innerHTML = renderJourneyMarkup();
  }

  const gamificationLive = root.querySelector("[data-bind='gamification-live']");
  if (gamificationLive) {
    gamificationLive.innerHTML = renderGamificationMarkup();
  }

  const coachLive = root.querySelector("[data-bind='coach-live']");
  if (coachLive) {
    coachLive.innerHTML = renderCoachMarkup();
  }

  const curriculumLive = root.querySelector("[data-bind='curriculum-live']");
  if (curriculumLive) {
    curriculumLive.innerHTML = renderCurriculumMarkup();
  }

  const sourcesLive = root.querySelector("[data-bind='sources-live']");
  if (sourcesLive) {
    sourcesLive.innerHTML = renderSourcesMarkup();
  }

  const reviewsLive = root.querySelector("[data-bind='reviews-live']");
  if (reviewsLive) {
    reviewsLive.innerHTML = renderReviewsMarkup();
  }

  const trainerOutput = root.querySelector("[data-bind='trainer-output']");
  if (trainerOutput && state.pendingReviews.length && !trainerOutput.dataset.filled) {
    trainerOutput.innerHTML = renderReviewsMarkup();
    trainerOutput.dataset.filled = "1";
  }

  const levelRing = document.querySelector("#level-pill .level-ring");
  if (levelRing) {
    levelRing.textContent = String(level);
  }
}

function renderStats() {
  const dashboard = state.dashboard || { mastered_questions: 0, wrong_answers: 0, xp: 0 };
  const stats = document.getElementById("app-stats");
  if (!stats) {
    return;
  }
  stats.innerHTML = `
    <span class="stat-chip">${dashboard.mastered_questions} gemeistert</span>
    <span class="stat-chip">${dashboard.wrong_answers} Fehler</span>
    <span class="stat-chip">${dashboard.xp || 0} XP</span>
  `;
}

function renderReportsMarkup() {
  return `
    <div class="report-list">
      ${
        state.trainingReports
          .map(
            (report) => `
          <article class="report-card card" data-report-id="${report.id}">
            <header>
              <strong>${escapeHtml(report.report_date)}</strong>
              <span>${report.hours} h · ${escapeHtml(report.status)}</span>
            </header>
            <p>${escapeHtml(report.activities)}</p>
            <div class="row-actions">
              ${
                report.status === "draft"
                  ? `<button class="primary-button" type="button" data-action="submit-report" data-report-id="${report.id}">Zur Unterschrift einreichen</button>`
                  : `<span class="badge ok">Eingereicht</span>`
              }
            </div>
          </article>`,
          )
          .join("") ||
        `<article class="card"><p class="muted">Noch keine Berichtsheft-Eintraege.</p>
          <a class="primary-button" href="/berichtsheft/neu" data-page-link>Ersten Eintrag schreiben</a></article>`
      }
    </div>`;
}

function renderUnitsMarkup() {
  if (!state.units.length) {
    return `<p class="muted">Keine Lerneinheiten geladen.</p>`;
  }
  return `<div class="question-list">${state.units
    .map(
      (unit) => `
      <a class="list-row" href="/lernen/einheit" data-page-link data-unit-slug="${escapeHtml(unit.slug)}">
        <strong>${escapeHtml(unit.title)}</strong>
        <span class="muted">Monat ${unit.month} · ${unit.estimated_minutes || "?"} Min · ${escapeHtml(unit.review_status)}</span>
      </a>`,
    )
    .join("")}</div>`;
}

function renderUnitDetailMarkup() {
  const unit = state.activeUnit;
  if (!unit) {
    return `<p class="muted">Lerneinheit waehlen.</p>
      <div data-bind-nested="units">${renderUnitsMarkup()}</div>`;
  }
  const theory = (unit.theory_blocks || [])
    .map(
      (block) => `
      <section class="card">
        <h3>${escapeHtml(block.heading)}</h3>
        <p>${escapeHtml(block.body)}</p>
        <ul class="plain-list">${(block.key_points || [])
          .map((point) => `<li>${escapeHtml(point)}</li>`)
          .join("")}</ul>
        <p class="muted">${escapeHtml((block.norm_references || []).join(" · "))}</p>
      </section>`,
    )
    .join("");
  const glossary = Object.entries(unit.glossary || {})
    .map(([term, definition]) => `<li><strong>${escapeHtml(term)}</strong> — ${escapeHtml(definition)}</li>`)
    .join("");
  return `
    <article class="card">
      <p class="eyebrow">Monat ${unit.month} · ${escapeHtml(unit.review_status)}</p>
      <h3>${escapeHtml(unit.title)}</h3>
      <p class="muted">${escapeHtml(unit.subtitle || "")}</p>
      <p><strong>Uebung:</strong> ${escapeHtml(unit.practice_task || "")}</p>
    </article>
    ${theory}
    <article class="card"><h3>Glossar</h3><ul class="plain-list">${glossary || "<li>Kein Glossar</li>"}</ul></article>
    <div class="row-actions">
      <a class="primary-button" href="/lernen/frage" data-page-link>Fragen ueben</a>
      <a class="secondary-button" href="/fachkunde" data-page-link>Zur Fachkunde</a>
    </div>`;
}

function renderJourneyMarkup() {
  if (!state.journey.length) {
    return `<p class="muted">Lernreise nicht geladen.</p>`;
  }
  return `<div class="path-map">${state.journey
    .slice(0, 12)
    .map((month) => {
      const done = month.total_categories > 0 && month.completed_categories >= month.total_categories;
      const cls = month.locked ? "locked" : done ? "done" : "active";
      return `<button class="path-node ${cls}" type="button" data-action="load-month" data-month="${month.month}">
        ${month.month} · ${escapeHtml(month.title || `Monat ${month.month}`)}
      </button>`;
    })
    .join("")}</div>`;
}

function renderGamificationMarkup() {
  const g = state.gamification || state.dashboard;
  if (!g) {
    return `<p class="muted">Gamification nach Login verfuegbar.</p>`;
  }
  const badges = (g.badges || []).map((badge) => `<li>${escapeHtml(badge)}</li>`).join("") ||
    "<li>Noch keine Badges</li>";
  const into = g.xp_into_level ?? (g.xp || 0) % 120;
  const per = g.xp_per_level || 120;
  return `
    <div class="metric-grid">
      <article class="metric-card card"><strong data-bind="level">${g.level}</strong><span>Level</span></article>
      <article class="metric-card card"><strong data-bind="xp">${g.xp}</strong><span>XP</span></article>
      <article class="metric-card card"><strong data-bind="streak">${g.streak_days || 0}</strong><span>Streak</span></article>
      <article class="metric-card card"><strong>${g.longest_streak_days || g.streak_days || 0}</strong><span>Longest</span></article>
    </div>
    <article class="card">
      <p>Fortschritt im Level: ${into} / ${per} XP</p>
      <div class="segmented-progress" aria-hidden="true">
        ${Array.from({ length: 5 }, (_, index) => {
          const filled = into / per > (index + 1) / 5;
          return `<span class="${filled ? "filled" : ""}"></span>`;
        }).join("")}
      </div>
      <h3>Badges</h3>
      <ul class="plain-list">${badges}</ul>
    </article>`;
}

function renderCoachMarkup() {
  const plan = state.coachPlan;
  if (!plan) {
    return `<p class="muted">Coach-Plan nach Login verfuegbar.</p>`;
  }
  return `
    <article class="card">
      <p>${escapeHtml(plan.greeting)}</p>
      <p><strong>Pruefungsreife:</strong> ${plan.readiness_percent}% · Fokus Monat ${plan.focus_month}</p>
    </article>
    <div class="chat-demo">
      ${(plan.tips || [])
        .map(
          (tip) => `
        <div class="chat-bubble bot">
          <strong>${escapeHtml(tip.title)}</strong><br>${escapeHtml(tip.body)}
          ${
            tip.action_href
              ? `<div><a href="${escapeHtml(tip.action_href)}" data-page-link>Oeffnen</a></div>`
              : ""
          }
        </div>`,
        )
        .join("")}
    </div>`;
}

function renderCurriculumMarkup() {
  if (!state.curriculum.length) {
    return `<p class="muted">Curriculum wird geladen…</p>`;
  }
  return `<ul class="plain-list">${state.curriculum
    .slice(0, 12)
    .map(
      (month) =>
        `<li><strong>Monat ${month.month}:</strong> ${escapeHtml(month.title)} (${escapeHtml(month.year || "")})</li>`,
    )
    .join("")}</ul>`;
}

function renderSourcesMarkup() {
  if (!state.sources.length) {
    return `<p class="muted">Quellen werden geladen…</p>`;
  }
  return `<ul class="plain-list">${state.sources
    .slice(0, 12)
    .map(
      (source) =>
        `<li><strong>${escapeHtml(source.title || source.key)}</strong> · ${escapeHtml(source.key)}</li>`,
    )
    .join("")}</ul>`;
}

function renderReviewsMarkup() {
  if (!STAFF_ROLES.has(state.role)) {
    return `<p class="muted">Review-Warteschlange nur fuer Staff-Rollen.</p>`;
  }
  if (!state.pendingReviews.length) {
    return `<p class="muted">Keine offenen Reviews.</p>`;
  }
  return `<div class="table-wrap"><table class="data-table">
    <thead><tr><th>Typ</th><th>Key</th><th>Titel</th><th>Status</th><th>Aktion</th></tr></thead>
    <tbody>
      ${state.pendingReviews
        .map(
          (row) => `
        <tr>
          <td>${escapeHtml(row.entity_type)}</td>
          <td>${escapeHtml(row.entity_key)}</td>
          <td>${escapeHtml(row.title)}</td>
          <td>${escapeHtml(row.review_status)}</td>
          <td class="row-actions">
            <button class="primary-button" type="button" data-action="review-decide" data-entity-type="${escapeHtml(row.entity_type)}" data-entity-key="${escapeHtml(row.entity_key)}" data-to-status="approved">Freigeben</button>
            <button class="secondary-button" type="button" data-action="review-decide" data-entity-type="${escapeHtml(row.entity_type)}" data-entity-key="${escapeHtml(row.entity_key)}" data-to-status="needs_revision">Nacharbeit</button>
          </td>
        </tr>`,
        )
        .join("")}
    </tbody>
  </table></div>`;
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
        <p>Offen: ${result.open_score}/${result.open_max_points} Punkte</p>
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
            <strong>${index + 1}. ${escapeHtml(question.prompt)}</strong>
            <div class="answer-options">
              ${question.options
                .map(
                  (option, optionIndex) => `
                    <button type="button" class="exam-answer-option ${
                      selected === optionIndex ? "selected" : ""
                    }" data-exam-action="choice" data-question-id="${question.question_id}" data-index="${optionIndex}">
                      ${optionIndex + 1}. ${escapeHtml(option)}
                    </button>`,
                )
                .join("")}
            </div>
          </li>`;
      })
      .join("");
    const openMarkup = (exam.open_questions || [])
      .slice(0, 5)
      .map((question, index) => {
        const saved = state.examOpenAnswers[question.question_id] || "";
        return `
          <li class="exam-question">
            <strong>Offen ${index + 1}. ${escapeHtml(question.prompt)}</strong>
            <p class="muted">Max. ${question.max_points} Punkte · ${escapeHtml(question.answer_format || "")}</p>
            <label class="field">
              <span>Antwort</span>
              <textarea data-open-answer="${question.question_id}" rows="3">${escapeHtml(saved)}</textarea>
            </label>
            <label class="field">
              <span>Selbsteinschaetzung (0–${question.max_points})</span>
              <input type="number" min="0" max="${question.max_points}" data-open-score="${question.question_id}" value="${question.max_points}" />
            </label>
            <button type="button" class="secondary-button" data-action="save-open-answer" data-question-id="${question.question_id}">Antwort speichern</button>
          </li>`;
      })
      .join("");
    target.innerHTML = `
      <div class="exam-session card">
        <div class="exam-session-header">
          <div><h3>${escapeHtml(exam.title)}</h3><p>${escapeHtml(exam.description)}</p></div>
          <div class="exam-session-meta">
            <span id="exam-timer">${formatExamTimer(state.examSession.expires_at)}</span>
            <span>Bestehen: ${state.examSession.passing_score_percent}%</span>
          </div>
        </div>
        <ol class="exam-list">${choiceMarkup}</ol>
        ${openMarkup ? `<h4>Offene Aufgaben</h4><ol class="exam-list">${openMarkup}</ol>` : ""}
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
        }>${escapeHtml(exam.title)}</option>`,
    )
    .join("");
  const exam = state.activeExam;
  target.innerHTML = `
    <label class="field"><span>Pruefung</span><select id="exam-select">${options}</select></label>
    <div class="exam-preview card">
      <h3>${escapeHtml(exam.title)}</h3>
      <p>${escapeHtml(exam.description)}</p>
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

async function saveExamOpenAnswer(questionId, root) {
  if (!state.examSession) {
    return;
  }
  const textarea = root.querySelector(`textarea[data-open-answer="${questionId}"]`);
  const scoreInput = root.querySelector(`input[data-open-score="${questionId}"]`);
  const learnerAnswer = String(textarea?.value || "").trim();
  if (learnerAnswer.length < 1) {
    throw new Error("Bitte eine offene Antwort eingeben.");
  }
  const selfScore = scoreInput ? Number(scoreInput.value) : null;
  await fetchJson(`/api/exams/sessions/${state.examSession.session_id}/open-answers`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      learner_answer: learnerAnswer,
      self_score: Number.isFinite(selfScore) ? selfScore : null,
    }),
  });
  state.examOpenAnswers[questionId] = learnerAnswer;
  showToast("Offene Antwort gespeichert");
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
  await refreshPrivateData();
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
  const activities = String(form.get("activities") || "").trim();
  if (activities.length < 10) {
    throw new Error("Taetigkeiten muessen mindestens 10 Zeichen haben.");
  }
  await fetchJson("/api/training-reports", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      report_date: String(form.get("report_date")),
      activities,
      hours: Number(form.get("hours")),
      status: "draft",
    }),
  });
  await refreshPrivateData();
  showToast("Berichtsheft-Eintrag gespeichert");
  await navigateTo("/berichtsheft");
}

async function submitTrainingReport(reportId) {
  await requireAuth();
  const report = state.trainingReports.find((item) => String(item.id) === String(reportId));
  if (!report) {
    throw new Error("Eintrag nicht gefunden.");
  }
  await fetchJson(`/api/training-reports/${reportId}`, {
    method: "PUT",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      report_date: report.report_date,
      activities: report.activities,
      hours: report.hours,
      status: "submitted",
    }),
  });
  await refreshPrivateData();
  showToast("Bericht eingereicht");
  await navigateTo("/berichtsheft/unterschrift");
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

async function recordConsent(accepted = true) {
  await requireAuth();
  await fetchJson("/api/privacy/consent", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ accepted }),
  });
  showToast(accepted ? "Datenschutz-Einwilligung gespeichert" : "Ablehnung gespeichert");
}

async function resetProgress() {
  await requireAuth();
  const confirmed = window.confirm("Fortschritt wirklich zuruecksetzen?");
  if (!confirmed) {
    return;
  }
  await fetchJson("/api/progress/reset", {
    method: "POST",
    headers: authHeaders(),
  });
  await refreshPrivateData();
  showToast("Fortschritt zurueckgesetzt");
}

async function loadUnitBySlug(slug) {
  state.activeUnit = await fetchJson(`/api/learning/units/${slug}`);
}

async function loadCurriculumBundle() {
  state.occupations = await fetchJson("/api/occupations").catch(() => []);
  const occupation =
    state.occupations.find((item) => item.slug === "maschinen-und-anlagenfuehrer") ||
    state.occupations[0];
  if (occupation) {
    state.curriculum = await fetchJson(
      `/api/occupations/${occupation.slug}/curriculum`,
    ).catch(() => []);
  }
  state.sources = await fetchJson("/api/sources").catch(() => []);
}

async function generateDraft() {
  requireStaff();
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
  const reviewed = await fetchJson("/api/content/review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      draft_id: draft.draft_id,
      approved: false,
      reviewer_notes: "Automatische Vorpruefung aus dem Trainer-Cockpit.",
    }),
  }).catch(() => draft);
  const output = document.querySelector("[data-bind='trainer-output']");
  if (output) {
    output.innerHTML = `
      <h3>${escapeHtml(reviewed.title)}</h3>
      <p><strong>Lernziel:</strong> ${escapeHtml(reviewed.learning_goal)}</p>
      <p>${escapeHtml(reviewed.fachkunde)}</p>
      <p><strong>Status:</strong> ${escapeHtml(reviewed.review_status)}</p>
      <p class="muted">Draft ${escapeHtml(reviewed.draft_id)}</p>`;
  }
}

async function loadReviews() {
  await requireAuth();
  requireStaff();
  state.pendingReviews = await fetchJson("/api/content/review/pending", {
    headers: authHeaders(),
  });
  const output =
    document.querySelector("[data-bind='reviews-live']") ||
    document.querySelector("[data-bind='trainer-output']");
  if (output) {
    output.innerHTML = renderReviewsMarkup();
  }
  showToast(`${state.pendingReviews.length} Reviews geladen`);
}

async function decideReview(entityType, entityKey, toStatus) {
  await requireAuth();
  requireStaff();
  await fetchJson("/api/content/review/decision", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      entity_type: entityType,
      entity_key: entityKey,
      to_status: toStatus,
      notes: toStatus === "approved" ? "Fachlich freigegeben." : "Bitte nacharbeiten.",
    }),
  });
  await loadReviews();
  showToast(toStatus === "approved" ? "Freigegeben" : "Zurueck an Autor");
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
  if (
    ["trainer", "admin"].includes(config.layout) &&
    state.accessToken &&
    !STAFF_ROLES.has(state.role)
  ) {
    showToast("Staff-Login erforderlich (reviewer-/trainer-/admin- Prefix).");
    await navigateTo("/mehr", false);
    return;
  }
  if (
    ["/lernen/einheit", "/fachkunde/einheit", "/fachkunde/bausteine"].includes(resolved.pathname)
  ) {
    if (!state.activeUnit && state.units[0]) {
      await loadUnitBySlug(state.units[0].slug).catch(() => null);
    }
  }
  if (
    ["/fachkunde/lernpfad", "/lernen/lernpfad", "/ausbilder/planung"].includes(resolved.pathname)
  ) {
    await loadCurriculumBundle();
  }
  if (["/gamification", "/gamification/xp", "/gamification/badges", "/gamification/streaks", "/fortschritt/xp"].includes(resolved.pathname) && state.accessToken) {
    state.gamification = await fetchJson("/api/gamification", { headers: authHeaders() }).catch(
      () => state.gamification,
    );
  }
  if (["/mehr/coach", "/mehr/lernplan"].includes(resolved.pathname) && state.accessToken) {
    state.coachPlan = await fetchJson("/api/coach/plan", { headers: authHeaders() }).catch(
      () => state.coachPlan,
    );
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
  state.activeExam =
    state.exams.find((exam) => exam.exam_id === "checkpoint-01") || state.exams[0] || null;
  await loadCurriculumBundle();
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
    if (target.dataset.action === "exam-start-shortcut" || target.id === "exam-start") {
      event.preventDefault();
      await startExamSession();
      return;
    }
    if (target.matches("[data-page-link]")) {
      event.preventDefault();
      if (target.dataset.qIndex) {
        state.currentQuestionIndex = Number(target.dataset.qIndex);
      }
      if (target.dataset.unitSlug) {
        await loadUnitBySlug(target.dataset.unitSlug);
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
    if (target.dataset.action === "privacy-consent") {
      await recordConsent(target.dataset.accepted !== "false");
      await navigateTo("/dashboard");
      return;
    }
    if (target.dataset.action === "reset-progress") {
      await resetProgress();
      return;
    }
    if (target.dataset.action === "submit-report") {
      await submitTrainingReport(target.dataset.reportId);
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
    if (target.dataset.action === "review-decide") {
      await decideReview(
        target.dataset.entityType,
        target.dataset.entityKey,
        target.dataset.toStatus,
      );
      return;
    }
    if (target.dataset.action === "load-month") {
      await loadLearnMonth(Number(target.dataset.month || "1"));
      showToast(`Monat ${state.learnMonth} geladen`);
      await navigateTo("/lernen", false);
      return;
    }
    if (target.dataset.action === "save-open-answer") {
      const root = target.closest(".exam-session") || document;
      await saveExamOpenAnswer(target.dataset.questionId, root);
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
      await navigateTo("/onboarding");
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

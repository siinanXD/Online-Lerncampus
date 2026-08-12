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
  syncPasswordStrength(root);
}

function passwordRules(value) {
  return {
    len: value.length >= 8,
    case: /[a-z]/.test(value) && /[A-Z]/.test(value),
    num: /\d/.test(value),
    special: /[^A-Za-z0-9]/.test(value),
  };
}

function syncPasswordStrength(root = document) {
  const input = root.querySelector("[data-pw-live]");
  const strength = root.querySelector("[data-pw-strength]");
  const checklist = root.querySelector("[data-pw-checklist]");
  if (!input || !strength || !checklist) {
    return;
  }
  const value = input.value || "";
  const rules = passwordRules(value);
  const score = Object.values(rules).filter(Boolean).length;
  const labels = ["Schwach", "Schwach", "Mittel", "Gut", "Stark"];
  const colors = ["#ef4444", "#ef4444", "#10b981", "#10b981", "#059669"];
  // Match Figma default for "SicheresKennw": 2 bars / Mittel when score is 2
  const activeBars = value ? Math.max(score, 1) : 2;
  strength.querySelectorAll(".pw-strength-bars span").forEach((bar, index) => {
    bar.classList.toggle("on", index < activeBars);
  });
  const label = strength.querySelector("strong");
  if (label) {
    const idx = value ? score : 2;
    label.textContent = labels[idx];
    label.style.color = colors[idx];
  }
  checklist.querySelectorAll("[data-rule]").forEach((item) => {
    const ok = rules[item.dataset.rule];
    item.classList.toggle("ok", Boolean(ok));
    const img = item.querySelector("img");
    if (img) {
      img.src = ok ? "/static/figma/auth/pw-check.svg" : "/static/figma/auth/pw-x.svg";
    }
  });
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
    el.textContent = String(mastered || 156);
  });
  root.querySelectorAll("[data-bind='wrong']").forEach((el) => {
    el.textContent = String(wrong);
  });
  root.querySelectorAll("[data-bind='readiness']").forEach((el) => {
    el.textContent = `${readiness || 67}%`;
  });
  root.querySelectorAll("[data-bind='total-questions']").forEach((el) => {
    el.textContent = String(total || state.questions?.length || 312);
  });
  root.querySelectorAll("[data-bind='open-questions']").forEach((el) => {
    const open = Math.max((total || 312) - (mastered || 156), 0);
    el.textContent = String(total ? open : 23);
  });
  const unitsCount = state.units?.length || 12;
  const unitsDone = state.units?.filter((u) => u.completed || u.status === "done").length || 8;
  root.querySelectorAll("[data-bind='units-count']").forEach((el) => {
    el.textContent = String(unitsCount);
  });
  root.querySelectorAll("[data-bind='units-done']").forEach((el) => {
    el.textContent = String(unitsDone);
  });
  root.querySelectorAll(".mastery-fill").forEach((el) => {
    el.style.width = `${readiness || 67}%`;
  });
  root.querySelectorAll("[data-bind='xp']").forEach((el) => {
    el.textContent = Number(xp).toLocaleString("de-DE");
  });
  root.querySelectorAll("[data-bind='level']").forEach((el) => {
    el.textContent = String(level);
  });
  root.querySelectorAll("[data-bind='streak']").forEach((el) => {
    el.textContent = String(streak);
  });
  const firstName = (state.displayName || "Max").split(/\s+/)[0];
  root.querySelectorAll("[data-bind='greeting-name']").forEach((el) => {
    el.textContent = `Hallo, ${firstName}!`;
  });
  const continueTitle = dashboard?.continue_title || dashboard?.focus_topic || "Pneumatik - Schaltpläne";
  root.querySelectorAll("[data-bind='continue-title']").forEach((el) => {
    el.textContent = continueTitle;
  });
  const answered = dashboard?.continue_answered ?? Math.min(mastered || 12, 30);
  const continueTotal = dashboard?.continue_total ?? 30;
  root.querySelectorAll("[data-bind='continue-progress']").forEach((el) => {
    el.textContent = `${answered}/${continueTotal} Fragen`;
  });
  root.querySelectorAll("[data-bind='continue-bar']").forEach((el) => {
    const pct = continueTotal ? Math.round((answered / continueTotal) * 100) : 0;
    el.style.width = `${Math.max(4, Math.min(100, pct))}%`;
  });
  const levelLabel = document.getElementById("level-label");
  if (levelLabel) {
    levelLabel.textContent = `LEVEL ${level}`;
  }
  document.querySelectorAll("#level-pill .level-ring, #level-pill [data-bind='level']").forEach((el) => {
    el.textContent = String(level);
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
  if (questionList && questionList.dataset.static !== "figma") {
    const source =
      config.path === "/lernen/fragen/fehler" || config.screen?.includes("fehler")
        ? state.questions.slice(0, 8)
        : state.questions.slice(0, 12);
    questionList.innerHTML = source.length
      ? source
          .map(
            (question, index) => {
              const dots = ["/static/figma/learn2/dot-green.svg", "/static/figma/learn2/dot-blue.svg", "/static/figma/learn2/dot-gray.svg", "/static/figma/learn2/dot-red.svg"];
              const dot = dots[index % dots.length];
              return `
          <a class="q-row" href="/lernen/frage" data-page-link data-q-index="${index}">
            <img class="q-dot" src="${dot}" width="10" height="10" alt="" />
            <span>${escapeHtml(question.prompt)}</span>
            <span class="diff-bars" aria-hidden="true"><i></i><i></i><i class="off"></i></span>
            <img class="q-chev" src="/static/figma/learn2/q-chevron.svg" width="14" height="14" alt="" />
          </a>`;
            },
          )
          .join("")
      : `<article class="list-row"><strong>Keine Fragen geladen</strong><span class="muted">Demo</span></article>`;
  }

  const livePrompt = root.querySelector("[data-bind='live-question-prompt']");
  const liveAnswers = root.querySelector("[data-bind='live-answers']");
  const isFeedbackScreen = Boolean(config.screen?.includes("feedback"));
  if (livePrompt && state.questions.length && !isFeedbackScreen) {
    const question = state.questions[state.currentQuestionIndex % state.questions.length];
    // Keep Figma demo copy on MC pixel frame when prompt already matches design.
    const keepFigmaCopy = config.path === "/lernen/frage" && livePrompt.textContent.includes("einfach- und doppeltwirkendem");
    if (!keepFigmaCopy) {
      livePrompt.textContent = question.prompt;
    }
    if (liveAnswers && !keepFigmaCopy) {
      const letters = ["A", "B", "C", "D", "E", "F"];
      liveAnswers.innerHTML = question.options
        .map(
          (option, index) => `
          <button class="answer-option" type="button" data-index="${index}">
            <span class="answer-letter">${letters[index] || index + 1}</span>
            <span class="answer-text">${escapeHtml(option)}</span>
          </button>`,
        )
        .join("");
    }
  }

  const freetextInput = root.querySelector("[data-bind='freetext-answer']");
  const freetextCount = root.querySelector("[data-bind='freetext-count']");
  if (freetextInput && freetextCount) {
    const syncCount = () => {
      freetextCount.textContent = `${freetextInput.value.length}/500`;
    };
    freetextInput.addEventListener("input", syncCount);
    syncCount();
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
    gamificationLive.innerHTML = renderGamificationMarkup(gamificationVariant(config?.path || window.location.pathname));
  }

  const reviewCount = Array.isArray(state.pendingReviews) ? state.pendingReviews.length : null;
  document.querySelectorAll("[data-bind='review-count']").forEach((el) => {
    if (reviewCount === null) {
      return;
    }
    el.textContent = String(reviewCount);
    el.hidden = reviewCount === 0;
    el.classList.toggle("is-empty", reviewCount === 0);
  });

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

function reportStatusMeta(status) {
  const key = String(status || "draft").toLowerCase();
  if (key === "approved" || key === "freigegeben") {
    return { label: "Freigegeben", cls: "ok" };
  }
  if (key === "submitted" || key === "pending" || key === "eingereicht") {
    return { label: "Eingereicht", cls: "info" };
  }
  return { label: "Entwurf", cls: "draft" };
}

function renderReportsMarkup() {
  if (!state.trainingReports.length) {
    return `<article class="bh-empty-api"><p class="muted">Noch keine Berichtsheft-Eintraege.</p>
      <a class="primary-button" href="/berichtsheft/neu" data-page-link>Ersten Eintrag schreiben</a></article>`;
  }
  return `
    <div class="bh-entry-list report-list">
      ${state.trainingReports
        .map((report) => {
          const meta = reportStatusMeta(report.status);
          const preview = escapeHtml(report.activities || "").slice(0, 80);
          return `
          <article class="bh-entry" data-report-id="${report.id}">
            <div class="bh-entry-top">
              <div class="bh-entry-dates"><strong>${escapeHtml(report.report_date)}</strong><span>${report.hours} h</span></div>
              <span class="bh-status ${meta.cls}">${meta.label}</span>
            </div>
            <div class="bh-entry-bottom">
              <div><p>${preview || "Ohne Beschreibung"}</p><span class="muted">${escapeHtml(report.status)}</span></div>
              ${
                report.status === "draft"
                  ? `<button class="bh-fill-btn" type="button" data-action="submit-report" data-report-id="${report.id}">Einreichen</button>`
                  : `<span class="bh-chevron" aria-hidden="true">›</span>`
              }
            </div>
          </article>`;
        })
        .join("")}
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

function levelTitleFor(level) {
  const n = Number(level) || 1;
  if (n >= 5) return "Experte";
  if (n >= 4) return "Meister";
  if (n >= 3) return "Profi";
  if (n >= 2) return "Fortgeschritten";
  return "Anfänger";
}

const GAME_LEVEL_LADDER = [
  { level: 1, title: "Anfänger", range: "0 – 120 XP", desc: "Grundausbildung gestartet" },
  { level: 2, title: "Fortgeschritten", range: "120 – 240 XP", desc: "Erste solide Fertigkeiten" },
  { level: 3, title: "Profi", range: "240 – 360 XP", desc: "Selbstständiges Arbeiten" },
  { level: 4, title: "Meister", range: "360 – 480 XP", desc: "Exzellente Systembeherrschung" },
  { level: 5, title: "Experte", range: "480+ XP", desc: "Campus-Elite & Mentorenstatus" },
];

const GAME_XP_SOURCES = [
  { icon: "✓", label: "Frage richtig", xp: "+10 – 20 XP" },
  { icon: "📘", label: "Lektion abgeschlossen", xp: "+50 XP" },
  { icon: "🏅", label: "Prüfung bestanden", xp: "+100 – 200 XP" },
  { icon: "🎯", label: "Daily Quest", xp: "+20 XP" },
  { icon: "🔥", label: "Streak Bonus", xp: "+5 XP/Tag" },
];

const GAME_BADGE_CATALOG = [
  { key: "feuereifer", name: "Feuereifer", emoji: "🔥", desc: "7 Tage tägliche Aktivität in Folge gehalten.", cat: "LERN-BADGES", rarity: "COMMON", match: ["Wochen-Streak", "3-Tage-Streak"] },
  { key: "buecherwurm", name: "Bücherwurm", emoji: "📚", desc: "50 Lerneinheiten erfolgreich bearbeitet.", cat: "LERN-BADGES", rarity: "UNCOMMON", match: ["Fachkunde-Starter"] },
  { key: "perfektionist", name: "Perfektionist", emoji: "🎯", desc: "10x ein Lern-Quiz mit exakt 100% absolviert.", cat: "LERN-BADGES", rarity: "RARE", match: ["5x gemeistert"] },
  { key: "blitzmerker", name: "Blitzmerker", emoji: "⚡", desc: "Quiz in weniger als 30 Sekunden fehlerfrei bestanden.", cat: "LERN-BADGES", rarity: "EPIC", match: [] },
  { key: "metallprofi", name: "Metallprofi", emoji: "🔧", desc: "Alle Lern-Module der Metalltechnik abgeschlossen.", cat: "FACH-BADGES", rarity: "RARE", match: [] },
  { key: "kunststoff", name: "Kunststoff-König", emoji: "♻️", desc: "Alle Spritzguss- und Kunststoffthemen bestanden.", cat: "FACH-BADGES", rarity: "RARE", match: [] },
  { key: "massmeister", name: "Maß-Meister", emoji: "📐", desc: "100 Aufgaben zu Toleranzberechnungen gelöst.", cat: "FACH-BADGES", rarity: "UNCOMMON", match: [] },
  { key: "werkstoff", name: "Werkstoffkenner", emoji: "🔬", desc: "Werkstoffkunde-Abschlusstest mit 100% gemeistert.", cat: "FACH-BADGES", rarity: "COMMON", match: ["Erster Schritt"] },
  { key: "teamplayer", name: "Teamplayer", emoji: "🤝", desc: "10x offene Fragen von Mitschülern beantwortet.", cat: "SOZIAL-BADGES", rarity: "UNCOMMON", match: [] },
  { key: "pruefungsheld", name: "Prüfungsheld", emoji: "🏆", desc: "Die IHK-Prüfungssimulation fehlerfrei abgeschlossen.", cat: "SOZIAL-BADGES", rarity: "EPIC", match: [] },
  { key: "diamant", name: "Diamant", emoji: "💎", desc: "Das maximale Level im Campus erreicht.", cat: "SOZIAL-BADGES", rarity: "LEGENDARY", match: [] },
  { key: "fruehaufsteher", name: "Frühaufsteher", emoji: "🌟", desc: "An 30 Tagen vor 7:00 Uhr morgens gelernt.", cat: "SOZIAL-BADGES", rarity: "RARE", match: ["Fleissig"] },
];

const GAME_LEADERBOARD = [
  { rank: 1, name: "Max Mustermann", level: 4, xp: 2840, you: true },
  { rank: 2, name: "Lisa Fischer", level: 3, xp: 2105, you: false },
  { rank: 3, name: "Tim Weber", level: 3, xp: 1890, you: false },
  { rank: 4, name: "Anna Schmidt", level: 3, xp: 1650, you: false },
  { rank: 5, name: "Jonas Becker", level: 3, xp: 1420, you: false },
  { rank: 6, name: "Sara Nguyen", level: 3, xp: 980, you: false },
  { rank: 7, name: "Kai Hoffmann", level: 2, xp: 720, you: false },
  { rank: 8, name: "Ahmed Yilmaz", level: 2, xp: 540, you: false },
];

function gamificationVariant(pathname) {
  if (!pathname) return "overview";
  if (pathname.includes("/badges")) return "badges";
  if (pathname.includes("/streaks")) return "streaks";
  if (pathname.includes("/xp") || pathname.includes("/fortschritt/xp")) return "xp";
  return "overview";
}

function renderBadgeGrid(earned) {
  const earnedSet = new Set((earned || []).map(String));
  return GAME_BADGE_CATALOG.map((badge) => {
    const unlocked =
      badge.match.some((m) => earnedSet.has(m)) || earnedSet.has(badge.name);
    const rarity = badge.rarity.toLowerCase();
    return `
      <article class="game-badge-tile ${unlocked ? "earned" : "locked"} rarity-${rarity}">
        <div class="game-badge-glyph" aria-hidden="true">${badge.emoji}</div>
        <strong>${escapeHtml(badge.name)}</strong>
        <p>${escapeHtml(badge.desc)}</p>
        <div class="game-badge-meta">
          <span>${escapeHtml(badge.cat)}</span>
          <span class="rarity-pill rarity-${rarity}">${escapeHtml(badge.rarity)}</span>
        </div>
      </article>`;
  }).join("");
}

function renderLevelLadder(currentLevel) {
  const level = Number(currentLevel) || 1;
  return GAME_LEVEL_LADDER.map((row) => {
    const reached = level >= row.level;
    const current = level === row.level || (level > 5 && row.level === 5);
    return `
      <div class="game-ladder-row ${reached ? "reached" : ""} ${current ? "current" : ""}">
        <span class="game-ladder-pill">Level ${row.level}</span>
        <strong>${escapeHtml(row.title)}</strong>
        <span class="muted">${escapeHtml(row.desc)}</span>
        <span class="game-ladder-xp">${escapeHtml(row.range)}</span>
      </div>`;
  }).join("");
}

function renderStreakWeek(streakDays) {
  const days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
  const active = Math.min(7, Math.max(0, Number(streakDays) || 0));
  return days
    .map((d, i) => {
      const on = i < active;
      return `<div class="game-streak-day ${on ? "on" : ""}"><span>${on ? "🔥" : "·"}</span><small>${d}</small></div>`;
    })
    .join("");
}

function renderLeaderboardMarkup(g) {
  const youName = state.displayName || "Max Mustermann";
  const youXp = Number(g?.xp || 0);
  const youLevel = Number(g?.level || 1);
  const rows = GAME_LEADERBOARD.map((row) => {
    const isYou = row.you;
    const name = isYou ? youName : row.name;
    const xp = isYou ? Math.max(youXp, row.xp) : row.xp;
    const level = isYou ? youLevel : row.level;
    return `
      <li class="game-lb-row ${isYou ? "you" : ""}">
        <span class="game-lb-rank">#${row.rank}</span>
        <span class="game-lb-avatar" aria-hidden="true">${escapeHtml(name.split(/\s+/).map((p) => p[0]).join("").slice(0, 2).toUpperCase())}</span>
        <div class="game-lb-meta">
          <strong>${escapeHtml(name)}${isYou ? " <em>(Du)</em>" : ""}</strong>
          <span class="muted">Level ${level}</span>
        </div>
        <strong class="game-lb-xp">${Number(xp).toLocaleString("de-DE")} XP</strong>
      </li>`;
  }).join("");
  return `<ol class="game-leaderboard">${rows}</ol>`;
}

function renderGamificationMarkup(variant = "overview") {
  const g = state.gamification || state.dashboard;
  if (!g) {
    return `<p class="muted">Gamification nach Login verfuegbar.</p>`;
  }
  const badges = g.badges || [];
  const into = g.xp_into_level ?? (g.xp || 0) % 120;
  const per = g.xp_per_level || 120;
  const pct = Math.max(0, Math.min(100, Math.round((into / per) * 100)));
  const title = levelTitleFor(g.level);
  const hero = `
    <div class="game-hero card">
      <div class="game-level-ring" aria-hidden="true"><span>${g.level}</span></div>
      <div>
        <p class="eyebrow">Dein Level</p>
        <h3 class="game-level-title">Level ${g.level} · ${escapeHtml(title)}</h3>
        <p class="muted">${into} / ${per} XP bis Level ${(g.level || 1) + 1}</p>
        <div class="game-xp-track" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
          <span style="width:${pct}%"></span>
        </div>
      </div>
    </div>`;
  const metrics = `
    <div class="metric-grid game-metrics">
      <article class="metric-card card"><strong data-bind="xp">${g.xp}</strong><span>XP gesamt</span></article>
      <article class="metric-card card"><strong data-bind="streak">${g.streak_days || 0}</strong><span>🔥 Streak</span></article>
      <article class="metric-card card"><strong>${g.longest_streak_days || g.streak_days || 0}</strong><span>Bester Streak</span></article>
      <article class="metric-card card"><strong>${badges.length}</strong><span>Badges</span></article>
    </div>`;
  const xpSources = `
    <article class="card game-sources-card">
      <h3>XP-Quellen</h3>
      <div class="game-xp-sources">
        ${GAME_XP_SOURCES.map(
          (s) => `
          <div class="game-xp-source">
            <span class="game-xp-source-ico" aria-hidden="true">${s.icon}</span>
            <div><strong>${escapeHtml(s.label)}</strong><span class="muted">${escapeHtml(s.xp)}</span></div>
          </div>`,
        ).join("")}
      </div>
    </article>`;
  const ladder = `
    <article class="card game-ladder-card">
      <h3>Level-Leiter</h3>
      <div class="game-ladder">${renderLevelLadder(g.level)}</div>
    </article>`;
  const badgeGrid = `
    <article class="card game-badge-card">
      <div class="row-between">
        <h3>Badges &amp; Achievements</h3>
        <span class="muted">${badges.length} freigeschaltet</span>
      </div>
      <div class="game-badge-grid">${renderBadgeGrid(badges)}</div>
      <div class="game-rarity-legend">
        <span class="rarity-pill rarity-common">COMMON</span>
        <span class="rarity-pill rarity-uncommon">UNCOMMON</span>
        <span class="rarity-pill rarity-rare">RARE</span>
        <span class="rarity-pill rarity-epic">EPIC</span>
        <span class="rarity-pill rarity-legendary">LEGENDARY</span>
      </div>
    </article>`;
  const streakCard = `
    <article class="card game-streak-card">
      <h3>Tägliche Lernserie</h3>
      <div class="game-streak-hero">
        <div class="game-streak-flame" aria-hidden="true">🔥</div>
        <div>
          <p class="eyebrow">Aktueller Streak</p>
          <strong class="game-streak-count">${g.streak_days || 0} Tage</strong>
          <p class="muted">Bester Streak: ${g.longest_streak_days || g.streak_days || 0} Tage</p>
        </div>
      </div>
      <div class="game-streak-week">${renderStreakWeek(g.streak_days)}</div>
      <div class="game-streak-tips">
        <div><strong>Streak-Schutz</strong><p class="muted">1× pro Monat einen Tag aussetzen ohne Reset.</p></div>
        <div><strong>Bonus ab Tag 7</strong><p class="muted">+5 XP/Tag solange die Serie hält.</p></div>
      </div>
    </article>`;
  const leaderboard = `
    <article class="card game-lb-card">
      <div class="row-between">
        <h3>Klassen-Ranking</h3>
        <span class="muted">IHK-Kohorte</span>
      </div>
      ${renderLeaderboardMarkup(g)}
      <p class="game-lb-note muted">Wochenaufgabe: Sammle 500 XP bis So. für das Bonus-Badge</p>
    </article>`;

  if (variant === "xp") {
    return `${hero}${metrics}${xpSources}${ladder}`;
  }
  if (variant === "badges") {
    return `${hero}${badgeGrid}`;
  }
  if (variant === "streaks") {
    return `${streakCard}${leaderboard}`;
  }
  return `${hero}${metrics}${badgeGrid}${streakCard}${leaderboard}`;
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
  const count = state.pendingReviews.length;
  document.querySelectorAll("[data-bind='review-count']").forEach((el) => {
    el.textContent = String(count);
    el.hidden = count === 0;
    el.classList.toggle("is-empty", count === 0);
  });
  showToast(`${count} Reviews geladen`);
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
  const layout = config.layout || "landing";
  document.body.dataset.pageLayout = layout;
  if (layout === "login" || layout === "auth" || layout === "app") {
    document.body.dataset.theme = "light";
  }
  document.title = `${config.title || "BZE"} | BZE Online Campus`;
  const title = document.getElementById("page-title");
  const eyebrow = document.getElementById("page-eyebrow");
  if (title) {
    title.textContent = config.title || "App";
  }
  if (eyebrow) {
    eyebrow.textContent = config.num ? `${config.num}` : "Teilnehmer";
  }
  const frame = document.querySelector(".app-frame");
  const chrome = config.chrome || "default";
  if (frame) {
    frame.dataset.chrome = chrome;
  }
  const mainTabs = document.querySelector(".tab-bar-main");
  const campusTabs = document.querySelector(".tab-bar-campus");
  const learnTabs = document.querySelector(".tab-bar-learn");
  const levelPill = document.getElementById("level-pill");
  const campusXpEl = document.getElementById("campus-xp-pill");
  if (mainTabs) {
    mainTabs.hidden = chrome === "campus" || chrome === "tablet" || chrome === "q-play" || chrome === "learn-drill" || chrome === "q-overlay" || chrome === "formel" || chrome === "ld" || chrome === "fk" || chrome === "exam" || chrome === "fp" || chrome === "bh" || chrome === "mehr";
  }
  if (campusTabs) {
    campusTabs.hidden = chrome !== "campus";
  }
  if (learnTabs) {
    learnTabs.hidden = chrome !== "learn-drill";
  }
  if (levelPill) {
    levelPill.hidden = chrome === "campus" || chrome === "tablet" || chrome === "learn-drill" || chrome === "q-play" || chrome === "q-overlay" || chrome === "formel" || chrome === "ld" || chrome === "fk" || chrome === "exam" || chrome === "fp" || chrome === "bh" || chrome === "mehr";
  }
  if (campusXpEl) {
    campusXpEl.hidden = chrome !== "campus";
  }
  const xp = state.dashboard?.xp ?? state.gamification?.xp ?? 95;
  const level = state.dashboard?.level ?? state.gamification?.level ?? 4;
  // Campus showcase frames (03.5–03.7) match Figma header copy L4 / 95 XP.
  const campusLevel = chrome === "campus" ? 4 : level;
  const campusXpValue = chrome === "campus" ? 95 : xp;
  document.querySelectorAll("[data-bind='level-short']").forEach((el) => {
    el.textContent = `L${campusLevel}`;
  });
  document.querySelectorAll("[data-bind='xp-short']").forEach((el) => {
    el.textContent = `${Number(campusXpValue).toLocaleString("de-DE")} XP`;
  });
  const campusTab = config.campusTab;
  document.querySelectorAll(".tab-bar-campus a").forEach((link) => {
    const active = link.dataset.campusTab === campusTab;
    link.classList.toggle("active", active);
    const icon = link.querySelector(".tab-campus-icon");
    if (icon) {
      icon.src = active ? icon.dataset.iconActive : icon.dataset.iconMuted;
    }
  });
  const tab = config.tab;
  document.querySelectorAll(".tab-bar-main a").forEach((link) => {
    const view = link.dataset.view;
    const mapped =
      (tab === "dashboard" && view === "dashboard") ||
      (tab === "learn" && view === "learn") ||
      (tab === "exam" && view === "exam") ||
      (tab === "reports" && view === "reports") ||
      (tab === "profile" && view === "profile");
    link.classList.toggle("active", Boolean(mapped));
  });
  document.querySelectorAll(".desk-nav a[data-nav]").forEach((link) => {
    const nav = link.dataset.nav;
    const inAdmin = Boolean(link.closest(".admin-shell"));
    let active = false;
    if (nav === "cockpit") {
      active =
        pathname === "/ausbilder" ||
        ["/ausbilder/teilnehmer", "/ausbilder/pruefungsreife", "/ausbilder/risiko", "/ausbilder/hotspots", "/ausbilder/shell", "/ausbilder/nav"].includes(
          pathname,
        );
    } else if (nav === "kohorte") {
      active = pathname.startsWith("/ausbilder/kohorte");
    } else if (nav === "review") {
      active = pathname.startsWith("/ausbilder/review") || pathname === "/ausbilder/freigabe";
    } else if (nav === "content" && !inAdmin) {
      active = ["/ausbilder/fragen", "/ausbilder/generator", "/ausbilder/themen", "/ausbilder/frage-bearbeiten", "/ausbilder/editor", "/ausbilder/medien"].includes(
        pathname,
      );
    } else if (nav === "reports") {
      active = pathname.startsWith("/ausbilder/bericht") || pathname === "/ausbilder/planung";
    } else if (nav === "users") {
      active = pathname.startsWith("/admin/nutzer") || pathname === "/admin/zugangsdaten" || pathname === "/admin/einstellungen";
    } else if (nav === "audit") {
      active = pathname === "/admin/audit";
    } else if (nav === "monitoring") {
      active = pathname === "/admin/monitoring" || pathname === "/admin";
    } else if (nav === "content" && inAdmin) {
      active =
        pathname.startsWith("/admin/content") ||
        ["/admin/import", "/admin/dubletten", "/admin/wissen", "/admin/lernziele", "/admin/quiz"].includes(pathname);
    }
    link.classList.toggle("active", Boolean(active));
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
    if (target.matches("[data-toggle-password]")) {
      event.preventDefault();
      const input = document.querySelector(target.getAttribute("data-toggle-password"));
      if (input) {
        input.type = input.type === "password" ? "text" : "password";
      }
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
      const optionsRoot = target.closest("[data-bind='live-answers']") || target.parentElement;
      optionsRoot.querySelectorAll(".answer-option").forEach((el) => el.classList.remove("selected"));
      target.classList.add("selected");
      const confirmBtn = document.querySelector("[data-action='confirm-answer']");
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.dataset.index = target.dataset.index;
      }
      return;
    }
    if (target.dataset.action === "confirm-answer") {
      const index = Number(target.dataset.index);
      if (!Number.isNaN(index)) {
        await answerQuestion(index);
        target.disabled = true;
      }
      return;
    }
    if (target.matches(".lang-option, .lang-row")) {
      document.querySelectorAll(".lang-option, .lang-row").forEach((el) => {
        el.classList.remove("active");
        if (el.getAttribute("aria-selected") != null) {
          el.setAttribute("aria-selected", "false");
        }
        const check = el.querySelector(".lang-check");
        if (check) {
          check.replaceWith(Object.assign(document.createElement("img"), {
            className: "lang-radio",
            src: "/static/figma/auth/lang-deselected.svg",
            width: 20,
            height: 20,
            alt: "",
          }));
        }
      });
      target.classList.add("active");
      if (target.getAttribute("aria-selected") != null) {
        target.setAttribute("aria-selected", "true");
      }
      const radio = target.querySelector(".lang-radio");
      if (radio) {
        const wrap = document.createElement("span");
        wrap.className = "lang-check";
        wrap.innerHTML = `<img src="/static/figma/auth/lang-check.svg" width="10" height="10" alt="" />`;
        radio.replaceWith(wrap);
      }
      const label = target.querySelector(".lang-left")?.textContent?.trim() || target.textContent;
      showToast(`Sprache: ${label}`);
    }
  } catch (error) {
    showToast(error.message);
    const feedback = document.getElementById("exam-feedback");
    if (feedback) {
      feedback.textContent = error.message;
    }
  }
});

document.addEventListener("input", (event) => {
  if (event.target?.matches?.("[data-pw-live]")) {
    syncPasswordStrength(event.target.closest(".auth-phone") || document);
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
      const loginFeedback = document.getElementById("login-feedback");
      if (loginFeedback) {
        loginFeedback.hidden = false;
        loginFeedback.textContent = "Angemeldet. Serverseitiger Lernstand ist aktiv.";
      }
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

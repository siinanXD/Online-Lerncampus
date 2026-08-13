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
  preferences: null,
  dailyGoal: null,
  authProfile: {
    requires_password_change: false,
    onboarding_completed: false,
    privacy_consent_accepted: false,
  },
  selectedLanguage: "de",
  formulas: [],
  diagnosisCases: [],
  activeDiagnosisSlug: null,
  videos: [],
  activeVideoSlug: null,
  videoTimer: null,
  notifications: [],
  notificationSettings: null,
  coachMessages: [],
  reportSuggest: null,
  caliperChoice: "23.5",
  injectionPhase: 0,
  currentQuestionIndex: 0,
  activeExam: null,
  examSession: null,
  examChoiceAnswers: {},
  examOpenAnswers: {},
  examResult: null,
  examProgress: null,
  examTimerHandle: null,
  lastAttempt: null,
  contentStats: null,
  levelUp: null,
  questionProgress: {},
  practiceFilter: "all",
  practiceMode: "all",
  allQuestions: [],
  examKindFilter: "alle",
  currentExamQuestionIndex: 0,
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

function isLoggedIn() {
  return Boolean(state.accessToken);
}

function liveNumber(value, demoFallback = 0) {
  if (isLoggedIn()) {
    return Number(value ?? 0);
  }
  return Number(value || demoFallback);
}

function livePercent(value, demoFallback = 0) {
  return `${liveNumber(value, demoFallback)}%`;
}

const EXAM_SHORTCUT_IDS = {
  zp: "MAF-ASSESS-ZP-SIM",
  ap: "MAF-ASSESS-AP-PT",
  diag: "MAF-ASSESS-DIAG-START",
};

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
  syncAuthProfile(session);
  await refreshPrivateData();
  return session;
}

function syncAuthProfile(profile = {}) {
  state.authProfile = {
    requires_password_change: Boolean(profile.requires_password_change),
    onboarding_completed: Boolean(profile.onboarding_completed),
    privacy_consent_accepted: Boolean(profile.privacy_consent_accepted),
  };
}

function resolvePostLoginRoute(profile = state.authProfile) {
  if (profile?.requires_password_change) {
    return "/passwort";
  }
  if (!profile?.onboarding_completed) {
    return "/sprache";
  }
  if (!profile?.privacy_consent_accepted) {
    return "/onboarding";
  }
  return "/dashboard";
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
  syncAuthProfile(state.profile);
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
  state.preferences = await fetchJson("/api/me/preferences", { headers: authHeaders() }).catch(
    () => null,
  );
  state.notificationSettings = await fetchJson("/api/me/notifications/settings", {
    headers: authHeaders(),
  }).catch(() => null);
  applyAppearance(state.preferences);
  state.dailyGoal = await fetchJson("/api/daily-goal", { headers: authHeaders() }).catch(() => null);
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
  bindPlatformTools(root, config);
  syncPasswordStrength(root);
  syncMehrPrivacyForms(root);
}

function syncMehrPrivacyForms(root = document) {
  const deleteBtn = root.querySelector(".dl-delete");
  const ack = root.querySelector("#dl-ack");
  const phrase = root.querySelector("#dl-phrase");
  const syncDelete = () => {
    if (!deleteBtn || !ack || !phrase) {
      return;
    }
    const ok = ack.checked && phrase.value.trim().toUpperCase() === "LÖSCHEN";
    deleteBtn.disabled = !ok;
  };
  if (ack && phrase && deleteBtn) {
    ack.addEventListener("change", syncDelete);
    phrase.addEventListener("input", syncDelete);
    syncDelete();
  }

  root.querySelectorAll(".de-opt").forEach((opt) => {
    opt.addEventListener("click", (event) => {
      event.preventDefault();
      const input = opt.querySelector('input[type="checkbox"]');
      if (!input) {
        return;
      }
      input.checked = !input.checked;
      opt.classList.toggle("on", input.checked);
      const box = opt.querySelector(".de-box");
      if (box) {
        box.innerHTML = input.checked
          ? '<img src="/static/figma/mehr/de-check.svg" width="12" height="12" alt="" />'
          : "";
      }
    });
  });

  root.querySelectorAll(".de-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      root.querySelectorAll(".de-tabs button").forEach((other) => other.classList.remove("on"));
      btn.classList.add("on");
    });
  });
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
  // Empty field: no bars; otherwise reflect live rule score.
  const activeBars = value ? Math.max(score, 1) : 0;
  strength.querySelectorAll(".pw-strength-bars span").forEach((bar, index) => {
    bar.classList.toggle("on", index < activeBars);
  });
  const label = strength.querySelector("strong");
  if (label) {
    const idx = value ? score : 0;
    label.textContent = labels[idx] || labels[0];
    label.style.color = colors[idx] || colors[0];
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
  const readinessRaw = dashboard?.readiness_percent ?? (total ? Math.round((mastered / total) * 100) : 0);
  const readiness = liveNumber(readinessRaw, 67);
  const xp = liveNumber(dashboard?.xp ?? state.gamification?.xp, 2450);
  const level = liveNumber(dashboard?.level ?? state.gamification?.level, 7);
  const streak = liveNumber(dashboard?.streak_days ?? state.gamification?.streak_days, 12);
  const badges = state.gamification?.badges || dashboard?.badges || [];
  const xpInto = dashboard?.xp_into_level ?? (xp % 120);
  const xpPer = dashboard?.xp_per_level || 120;
  const xpPct = Math.max(0, Math.min(100, Math.round((xpInto / xpPer) * 100)));

  root.querySelectorAll("[data-bind='mastered']").forEach((el) => {
    el.textContent = String(liveNumber(mastered, 156));
  });
  root.querySelectorAll("[data-bind='wrong']").forEach((el) => {
    el.textContent = String(liveNumber(wrong, isLoggedIn() ? 0 : 3));
  });
  root.querySelectorAll(".ov-screen [data-bind='wrong']").forEach((el) => {
    el.textContent = String(liveNumber(wrong, 3));
  });
  root.querySelectorAll("[data-bind='readiness']").forEach((el) => {
    el.textContent = livePercent(readinessRaw, 67);
  });
  root.querySelectorAll("[data-bind='total-questions']").forEach((el) => {
    el.textContent = String(liveNumber(total || state.questions?.length || state.allQuestions?.length, 480));
  });
  root.querySelectorAll("[data-bind='open-questions']").forEach((el) => {
    const openCount = Number(dashboard?.open_questions);
    const fallback = Math.max(liveNumber(total, 312) - liveNumber(mastered, 156), 0);
    el.textContent = String(Number.isFinite(openCount) ? openCount : (isLoggedIn() ? fallback : fallback || 23));
  });
  root.querySelectorAll("[data-bind='correct-once']").forEach((el) => {
    el.textContent = String(Number(dashboard?.correct_once_questions) || 0);
  });
  root.querySelectorAll("[data-bind='wrong-questions']").forEach((el) => {
    el.textContent = String(Number(dashboard?.wrong_questions) || 0);
  });
  const unitsCount = state.units?.length || dashboard?.units_total || 12;
  const unitsDone =
    state.units?.filter((u) => u.completed || u.status === "done").length ||
    dashboard?.units_completed ||
    0;
  root.querySelectorAll("[data-bind='units-count']").forEach((el) => {
    el.textContent = String(unitsCount);
  });
  root.querySelectorAll("[data-bind='units-done']").forEach((el) => {
    el.textContent = String(unitsDone);
  });
  root.querySelectorAll(".mastery-fill").forEach((el) => {
    el.style.width = `${liveNumber(readinessRaw, 67)}%`;
  });
  root.querySelectorAll("[data-bind='readiness-bar']").forEach((el) => {
    el.style.width = `${liveNumber(readinessRaw, 67)}%`;
  });
  root.querySelectorAll("[data-bind='xp-bar-fill']").forEach((el) => {
    el.style.width = `${xpPct}%`;
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
  root.querySelectorAll(".ov-screen [data-bind='streak']").forEach((el) => {
    el.textContent = String(streak);
  });
  root.querySelectorAll(".ov-screen [data-bind='xp']").forEach((el) => {
    el.textContent = Number(xp).toLocaleString("de-DE");
  });
  root.querySelectorAll(".ov-header [data-bind='level']").forEach((el) => {
    el.textContent = String(level);
  });
  const firstName = (state.displayName || (isLoggedIn() ? "Azubi" : "Max")).split(/\s+/)[0];
  root.querySelectorAll("[data-bind='first-name']").forEach((el) => {
    el.textContent = firstName;
  });
  root.querySelectorAll("[data-bind='greeting-name']").forEach((el) => {
    el.textContent = `Hallo, ${firstName}!`;
  });
  root.querySelectorAll("[data-bind='level-label']").forEach((el) => {
    el.textContent = `Level ${level}`;
  });
  root.querySelectorAll(".gx-level-pill.soft").forEach((el) => {
    el.textContent = `Level ${level} Lehrling`;
  });
  root.querySelectorAll("[data-bind='streak-days']").forEach((el) => {
    el.textContent = `${streak} Tage`;
  });
  root.querySelectorAll("[data-bind='profile-name']").forEach((el) => {
    el.textContent = state.displayName || (isLoggedIn() ? "Azubi" : "Max Müller");
  });
  root.querySelectorAll("[data-bind='xp-num']").forEach((el) => {
    el.textContent = Number(xp).toLocaleString("de-DE");
  });
  root.querySelectorAll("[data-bind='xp-level']").forEach((el) => {
    const nextLevelXp = xpPer * level;
    el.textContent = `${Number(xp).toLocaleString("de-DE")} / ${Number(nextLevelXp).toLocaleString("de-DE")} XP`;
  });
  root.querySelectorAll("[data-bind='readiness-pct']").forEach((el) => {
    el.textContent = livePercent(dashboard?.readiness_percent ?? readinessRaw, 67);
  });
  root.querySelectorAll("[data-bind='badge-count']").forEach((el) => {
    el.textContent = String(badges.length);
  });
  const languageLabels = { de: "Deutsch", en: "English", tr: "Türkçe", ar: "العربية", uk: "Українська" };
  const languageKey = state.preferences?.language || state.selectedLanguage || "de";
  root.querySelectorAll("[data-bind='language-label']").forEach((el) => {
    el.textContent = languageLabels[languageKey] || "Deutsch";
  });
  const reports = state.trainingReports || [];
  const reportsDone = reports.filter((item) =>
    ["approved", "submitted", "freigegeben", "eingereicht"].includes(String(item.status || "").toLowerCase()),
  ).length;
  const reportsTarget = 24;
  const reportsMissing = Math.max(reportsTarget - reports.length, 0);
  root.querySelectorAll("[data-bind='report-summary']").forEach((el) => {
    el.textContent = reports.length
      ? `Ausbildungsnachweis ${reportsDone} von ${reportsTarget} Wochen gepflegt`
      : "Noch keine Berichtsheft-Einträge";
  });
  root.querySelectorAll("[data-bind='report-missing']").forEach((el) => {
    el.textContent = reports.length ? `${reportsMissing} fehlen` : "Offen";
  });
  root.querySelectorAll("[data-bind='journey-pct']").forEach((el) => {
    el.textContent = `${journeyCompletionPercent()}% abgeschlossen`;
  });
  root.querySelectorAll("[data-bind='journey-month-title']").forEach((el) => {
    const month = state.journey.find((entry) => entry.month === state.learnMonth);
    el.textContent = month?.title || `Monat ${state.learnMonth}`;
  });
  const continueTitle =
    currentLearnUnit()?.title ||
    dashboard?.continue_title ||
    dashboard?.focus_topic ||
    (isLoggedIn() ? "Weiterlernen" : "Pneumatik — Schaltpläne");
  const nextUnit = currentLearnUnit();
  root.querySelectorAll("[data-action='open-unit']").forEach((el) => {
    if (!el.dataset.unitSlug && nextUnit?.slug) {
      el.dataset.unitSlug = nextUnit.slug;
    }
  });
  root.querySelectorAll("[data-bind='continue-title']").forEach((el) => {
    el.textContent = continueTitle;
  });
  const continueUnit = currentLearnUnit();
  if (continueUnit) {
    const monthUnits = learnUnitsForMonth(continueUnit.month);
    const position = Math.max(
      1,
      monthUnits.findIndex((item) => item.slug === continueUnit.slug) + 1,
    );
    root.querySelectorAll("[data-bind='continue-unit-meta']").forEach((el) => {
      el.textContent = `Lerneinheit ${position} von ${monthUnits.length || 10} · Monat ${continueUnit.month}`;
    });
  }
  const journeyMonth = currentJourneyMonth();
  root.querySelectorAll("[data-bind='occupation-line']").forEach((el) => {
    const year = journeyMonth >= 13 ? "2. Lehrjahr" : "1. Lehrjahr";
    el.textContent = `Maschinen- und Anlagenführer — ${year}`;
  });
  const answered = liveNumber(dashboard?.continue_answered, isLoggedIn() ? 0 : 12);
  const continueTotal = liveNumber(dashboard?.continue_total, isLoggedIn() ? total || 30 : 30);
  root.querySelectorAll("[data-bind='continue-progress']").forEach((el) => {
    el.textContent =
      el.dataset.format === "compact"
        ? `${answered}/${continueTotal} Fragen`
        : `${answered} / ${continueTotal} Fragen`;
  });
  root.querySelectorAll("[data-bind='continue-bar']").forEach((el) => {
    const pct = continueTotal ? Math.round((answered / continueTotal) * 100) : 0;
    el.style.width = `${Math.max(4, Math.min(100, pct))}%`;
  });
  const dailyDone = dashboard?.daily_lessons_done ?? state.dailyGoal?.lessons_completed ?? 0;
  const dailyTarget = dashboard?.daily_lessons_goal ?? state.dailyGoal?.lessons_goal ?? 5;
  const dailyLeft = Math.max(dailyTarget - dailyDone, 0);
  root.querySelectorAll("[data-bind='daily-goal']").forEach((el) => {
    el.textContent =
      el.dataset.format === "meta"
        ? `${dailyDone} von ${dailyTarget} Lektionen heute`
        : `Tagesziel: ${dailyDone} von ${dailyTarget} Lektionen`;
  });
  const dailyPct = dailyTarget ? Math.round((Math.min(dailyDone, dailyTarget) / dailyTarget) * 100) : 0;
  root.querySelectorAll("[data-bind='daily-pct']").forEach((el) => {
    el.textContent = `${dailyPct}%`;
  });
  root.querySelectorAll(".ov-screen [data-bind='daily-goal']").forEach((el) => {
    el.textContent = `${dailyDone} von ${dailyTarget} Lektionen heute`;
  });
  root.querySelectorAll("[data-bind='daily-remaining']").forEach((el) => {
    if (!dailyLeft) {
      el.textContent = "Tagesziel erreicht!";
      return;
    }
    el.textContent =
      el.dataset.format === "short"
        ? `Noch ${dailyLeft} für dein Tagesziel`
        : `Noch ${dailyLeft} Lektionen bis zum Tagesbonus (+50 XP)!`;
  });
  root.querySelectorAll(".ov-screen [data-bind='daily-remaining']").forEach((el) => {
    const left = Math.max(dailyTarget - dailyDone, 0);
    el.textContent = left ? `Noch ${left} für dein Tagesziel` : "Tagesziel erreicht!";
  });
  root.querySelectorAll("[data-bind='daily-segments']").forEach((el) => {
    const n = Math.max(1, Number(dailyTarget) || 5);
    const done = Math.max(0, Math.min(Number(dailyDone) || 0, n));
    el.innerHTML = Array.from({ length: n }, (_, i) =>
      `<span${i < done ? ' class="filled"' : ""}></span>`,
    ).join("");
  });
  root.querySelectorAll(".ov-screen [data-bind='daily-segments']").forEach((el) => {
    const n = Math.max(1, Number(dailyTarget) || 5);
    const done = Math.max(0, Math.min(Number(dailyDone) || 0, n));
    el.innerHTML = Array.from({ length: n }, (_, i) =>
      `<span${i < done ? ' class="filled"' : ""}></span>`,
    ).join("");
  });
  root.querySelectorAll("[data-bind='level-caps']").forEach((el) => {
    el.textContent = `LEVEL ${level}`;
  });
  const minutesToday = dashboard?.study_minutes_today ?? state.dailyGoal?.minutes_studied ?? 0;
  const minutesWeek = dashboard?.study_minutes_week ?? state.dailyGoal?.minutes_studied_week ?? 0;
  root.querySelectorAll("[data-bind='study-minutes']").forEach((el) => {
    el.textContent = `${minutesToday} Min`;
  });
  root.querySelectorAll(".ov-screen [data-bind='study-minutes']").forEach((el) => {
    el.textContent = `${minutesToday} Min`;
  });
  root.querySelectorAll("[data-bind='week-total']").forEach((el) => {
    const hours = Math.floor(minutesWeek / 60);
    const mins = minutesWeek % 60;
    el.textContent = hours ? `${hours}h ${mins}min diese Woche` : `${mins}min diese Woche`;
  });
  root.querySelectorAll(".ov-screen [data-bind='week-total']").forEach((el) => {
    if (isLoggedIn() || minutesWeek) {
      const hours = Math.floor(minutesWeek / 60);
      const mins = minutesWeek % 60;
      el.textContent = hours ? `${hours}h ${mins}min diese Woche` : `${mins}min diese Woche`;
    }
  });
  const weekMinutes = Array.isArray(dashboard?.week_minutes)
    ? dashboard.week_minutes
    : [0, 0, 0, 0, 0, 0, 0];
  const weekLabels = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
  const weekMax = Math.max(...weekMinutes, 1);
  const gxWeekDays = root.querySelector("[data-bind='gx-week-days']");
  if (gxWeekDays) {
    gxWeekDays.innerHTML = weekLabels
      .map((label, index) => {
        const mins = Number(weekMinutes[index]) || 0;
        return `<div class="gx-day${mins ? " done" : ""}"><i></i><span>${label}</span></div>`;
      })
      .join("");
  }
  root.querySelectorAll("[data-bind='week-bars-live']").forEach((el) => {
    el.innerHTML = weekLabels
      .map((label, index) => {
        const mins = Number(weekMinutes[index]) || 0;
        const height = mins ? Math.max(8, Math.round((mins / weekMax) * 55)) : 4;
        const emptyClass = mins ? "" : ' class="empty"';
        return `<div class="week-bar"><i${emptyClass} style="height:${height}px"></i><span>${label}</span></div>`;
      })
      .join("");
  });
  const reviewTopic =
    dashboard?.review_topic ||
    (dashboard?.weak_categories?.[0]
      ? categorySlugToTitle(String(dashboard.weak_categories[0].category_slug))
      : "");
  root.querySelectorAll("[data-bind='review-topic']").forEach((el) => {
    el.textContent = reviewTopic ? `Wiederholung: ${reviewTopic}` : "Wiederholung";
  });
  root.querySelectorAll(".level-ring-progress").forEach((el) => {
    const pct = xpPer ? Math.max(0, Math.min(100, Math.round((xpInto / xpPer) * 100))) : 0;
    el.style.opacity = `${0.35 + pct / 200}`;
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
  if (questionList) {
    renderPracticeQuestionList(root, config, questionList);
  }

  const livePrompt = root.querySelector("[data-bind='live-question-prompt'], .ld-prompt");
  const liveAnswers = root.querySelector("[data-bind='live-answers'], .ld-answers");
  const isFeedbackScreen = Boolean(config.screen?.includes("feedback"));
  const isLearnQuestionScreen = ["/lernen/frage", "/lernen/detail"].includes(config.path);
  if (livePrompt && state.questions.length && !isFeedbackScreen && isLearnQuestionScreen) {
    const question = state.questions[state.currentQuestionIndex % state.questions.length];
    livePrompt.textContent = question.prompt;
    if (liveAnswers) {
      const letters = ["A", "B", "C", "D", "E", "F"];
      liveAnswers.innerHTML = question.options
        .map(
          (option, index) => `
          <button class="${liveAnswers.matches(".ld-answers") ? "ld-answer" : "answer-option"}" type="button" data-index="${index}">
            <span class="${liveAnswers.matches(".ld-answers") ? "ld-letter" : "answer-letter"}">${letters[index] || index + 1}</span>
            <span>${escapeHtml(option)}</span>
          </button>`,
        )
        .join("");
    }
    const ldCounter = root.querySelector(".ld-counter");
    if (ldCounter && state.questions.length) {
      ldCounter.textContent = `Frage ${state.currentQuestionIndex + 1} von ${state.questions.length}`;
    }
    const topicPill = root.querySelector(".q-meta-row .topic-pill");
    if (topicPill) {
      topicPill.textContent = categoryDisplayTitle(question.category_slug || "Fachkunde");
    }
    const tracker = root.querySelector("[data-bind='q-tracker']");
    if (tracker) {
      tracker.textContent = `${state.currentQuestionIndex + 1}/${state.questions.length}`;
    }
    const fill = root.querySelector(".q-progress-fill");
    if (fill && state.questions.length) {
      fill.style.width = `${Math.round(((state.currentQuestionIndex + 1) / state.questions.length) * 100)}%`;
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

  const gxJourneyLive = root.querySelector("[data-bind='gx-journey-live']");
  if (gxJourneyLive) {
    gxJourneyLive.innerHTML = renderGxJourneyLive();
  }

  const gxBadgesLive = root.querySelector("[data-bind='gx-badges-live']");
  if (gxBadgesLive) {
    gxBadgesLive.innerHTML = renderGxBadgesLive(badges);
  }

  const gxJourneySummary = root.querySelector("[data-bind='gx-journey-summary-live']");
  if (gxJourneySummary) {
    gxJourneySummary.innerHTML = renderGxJourneySummary();
  }

  bindExamLiveScreens(root, config);
  bindExamHub(root, config);
  bindExamResultScreens(root, config);
  bindExamWeakTopics(root, config);
  bindLearnPractice(root, config);
  bindGxLearnScreen(root, config);
  bindFachkundeScreens(root, config);
  bindProgressScreens(root, config);
  bindAuthScreens(root, config);
  bindLevelUpScreen(root, config);

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
    return `<p class="muted">Lerneinheit wählen.</p>
      <div data-bind-nested="units">${renderUnitsMarkup()}</div>`;
  }
  const theory = (unit.theory_blocks || [])
    .map(
      (block) => `
      <article class="gx-card">
        <p class="gx-kicker">${escapeHtml(block.heading || "Fachkunde")}</p>
        <strong>${escapeHtml(block.heading || unit.title)}</strong>
        <p>${escapeHtml(block.body || "")}</p>
        <ul class="gx-key-list">${(block.key_points || [])
          .map((point) => `<li>${escapeHtml(point)}</li>`)
          .join("")}</ul>
        ${(block.norm_references || []).length
          ? `<p class="muted">${escapeHtml(block.norm_references.join(" · "))}</p>`
          : ""}
      </article>`,
    )
    .join("");
  const glossaryEntries = Object.entries(unit.glossary || {});
  const glossary = glossaryEntries.length
    ? `<article class="gx-card">
        <p class="gx-kicker">Glossar</p>
        <ul class="gx-key-list">${glossaryEntries
          .map(([term, definition]) => `<li><strong>${escapeHtml(term)}</strong> — ${escapeHtml(definition)}</li>`)
          .join("")}</ul>
        <a class="gx-chip" href="/lernen/glossar" data-page-link>Alle Begriffe</a>
      </article>`
    : "";
  return `
    <article class="gx-card gx-continue">
      <p class="gx-kicker">Monat ${unit.month} · Einheit ${unit.position || 1}</p>
      <strong>${escapeHtml(unit.title)}</strong>
      <p>${escapeHtml(unit.subtitle || unit.practice_task || "")}</p>
    </article>
    ${theory || `<article class="gx-card"><p>${escapeHtml(unit.practice_task || "Keine Theorie hinterlegt.")}</p></article>`}
    ${glossary}
    <div class="gx-section">
      <p class="gx-section-label">WEITERLERNEN</p>
      <div class="gx-chips">
        <a class="gx-chip" href="/lernen/frage" data-page-link data-action="start-unit" data-unit-slug="${escapeHtml(unit.slug)}">Fragen üben</a>
        <a class="gx-chip" href="/lernen/formeltrainer" data-page-link>Formeltrainer</a>
        <a class="gx-chip" href="/lernen/video" data-page-link>Video</a>
        <a class="gx-chip" href="/lernen/fehlerdiagnose" data-page-link>Fehlerdiagnose</a>
        <a class="gx-chip" href="/fachkunde/einheit" data-page-link data-unit-slug="${escapeHtml(unit.slug)}">Fachkunde</a>
      </div>
    </div>`;
}

function journeyCompletionPercent() {
  if (!state.journey.length) {
    return 0;
  }
  const totals = state.journey.reduce(
    (acc, month) => {
      acc.completed += month.completed_categories || 0;
      acc.total += month.total_categories || 0;
      return acc;
    },
    { completed: 0, total: 0 },
  );
  return totals.total ? Math.round((totals.completed / totals.total) * 100) : 0;
}

function allLearnUnits() {
  return [...(state.units || [])].sort(
    (a, b) => (Number(a.month) || 0) - (Number(b.month) || 0) || (a.position || 0) - (b.position || 0),
  );
}

function learnUnitsForMonth(month = state.learnMonth || 1) {
  return allLearnUnits().filter((unit) => Number(unit.month) === Number(month));
}

function currentLearnUnit() {
  return allLearnUnits().find((unit) => !unit.completed) || allLearnUnits()[0] || null;
}

function unitXpReward(unit, isCurrent) {
  if (isCurrent) {
    return 40;
  }
  return Math.max(20, Number(unit?.estimated_minutes) || 30);
}

function renderGxJourneyLive() {
  const units = allLearnUnits();
  if (!units.length) {
    return `<p class="muted">Keine Lerneinheiten geladen.</p>`;
  }
  const firstOpen = units.findIndex((unit) => !unit.completed);
  const currentIndex = firstOpen < 0 ? units.length - 1 : firstOpen;
  const months = [...new Set(units.map((unit) => Number(unit.month) || 1))];
  const journeyByMonth = Object.fromEntries(
    (state.journey || []).map((entry) => [Number(entry.month), entry]),
  );
  return months
    .map((month) => {
      const monthUnits = units.filter((unit) => Number(unit.month) === month);
      const meta = journeyByMonth[month] || {};
      const title = meta.title || `Monat ${month}`;
      const doneCount = monthUnits.filter((unit) => unit.completed).length;
      const lockedMonth = monthUnits.every((unit) => {
        const index = units.findIndex((item) => item.slug === unit.slug);
        return !unit.completed && index > currentIndex;
      });
      const header = `
        <div class="gx-path-month${lockedMonth ? " is-locked" : ""}">
          <span>Monat ${month}${meta.checkpoint ? " · Checkpoint" : ""}</span>
          <strong>${escapeHtml(title)}</strong>
          <em>${doneCount}/${monthUnits.length} Einheiten</em>
        </div>`;
      const nodes = monthUnits
        .map((unit) => {
          const index = units.findIndex((item) => item.slug === unit.slug);
          const side = index % 2 === 0 ? "left" : "right";
          const done = Boolean(unit.completed);
          const locked = !done && index > currentIndex;
          const isCurrent = !done && index === currentIndex;
          const nodeClass = done ? "done" : isCurrent ? "current" : "locked";
          const icon = done
            ? `<img src="/static/figma/gx/check.svg" width="24" height="24" alt="" />`
            : locked
              ? `<img src="/static/figma/gx/lock.svg" width="22" height="22" alt="" />`
              : `<img src="/static/figma/gx/target.svg" width="24" height="24" alt="" />`;
          const xp = unitXpReward(unit, isCurrent);
          const status = done ? `+${xp} XP` : locked ? "Noch gesperrt" : `+${xp} XP`;
          const action = locked
            ? `type="button" data-action="toast" data-toast="Noch gesperrt"`
            : `href="/lernen/einheit" data-page-link data-action="open-unit" data-unit-slug="${escapeHtml(unit.slug)}"`;
          const tag = locked ? "button" : "a";
          return `
        <${tag} class="gx-path-row ${side}${locked ? " is-locked" : ""}" ${action}>
          ${side === "left" ? `<div class="gx-node ${nodeClass}">${icon}</div>` : ""}
          <div class="gx-node-text${side === "right" ? " end" : ""}">
            <strong>${escapeHtml(unit.title)}</strong>
            <span class="${done ? "ok" : locked ? "muted" : "now"}">${escapeHtml(status)}</span>
          </div>
          ${side === "right" ? `<div class="gx-node ${nodeClass}">${icon}</div>` : ""}
        </${tag}>`;
        })
        .join("");
      return header + nodes;
    })
    .join("");
}

function renderGxBadgesLive(earned) {
  const earnedSet = new Set((earned || []).map(String));
  const tiles = GAME_BADGE_CATALOG.slice(0, 8).map((badge) => {
    const unlocked =
      badge.match.some((label) => earnedSet.has(label)) || earnedSet.has(badge.name);
    return `<div class="gx-badge ${unlocked ? "on" : "off"}"><i>${badge.emoji}</i><span>${escapeHtml(badge.name)}</span></div>`;
  });
  return `<div class="gx-badge-row">${tiles.slice(0, 4).join("")}</div><div class="gx-badge-row">${tiles.slice(4, 8).join("")}</div>`;
}

function renderGxJourneySummary() {
  if (!state.journey.length) {
    return `<p class="muted">Lernreise nach Login verfügbar.</p>`;
  }
  const chunks = [
    { title: "Grundlagen & Einstieg", months: state.journey.slice(0, 8) },
    { title: "Zwischenprüfungsvorbereitung", months: state.journey.slice(8, 12) },
    { title: "Vertiefung & Abschluss", months: state.journey.slice(12, 24) },
  ];
  return chunks
    .map((chunk) => {
      const total = chunk.months.reduce((sum, month) => sum + (month.total_categories || 0), 0);
      const done = chunk.months.reduce((sum, month) => sum + (month.completed_categories || 0), 0);
      const pct = total ? Math.round((done / total) * 100) : 0;
      const icon =
        pct >= 100 ? "check-circle.svg" : pct > 0 ? "fp-clock.svg" : "fp-lock.svg";
      const status = pct >= 100 ? "Erledigt" : pct > 0 ? `In Arbeit (${pct}%)` : "Nicht gestartet";
      return `
        <a class="gx-path-item${pct <= 0 ? " muted" : ""}" href="/lernen" data-page-link>
          <img src="/static/figma/gx/${icon}" width="18" height="18" alt="" />
          <div><strong>${escapeHtml(chunk.title)}</strong><span>${escapeHtml(status)}</span></div>
        </a>`;
    })
    .join("");
}

function getCurrentExamQuestion() {
  const exam = state.examSession?.exam;
  const questions = exam?.questions || [];
  if (!questions.length) {
    return null;
  }
  const progressId = state.examProgress?.current_question_id;
  if (progressId) {
    return (
      questions.find((question) => question.question_id === progressId) ||
      questions[state.currentExamQuestionIndex] ||
      questions[0]
    );
  }
  return questions[state.currentExamQuestionIndex] || questions[0];
}

function syncExamStateFromProgress(progress) {
  state.examProgress = progress;
  state.currentExamQuestionIndex = Math.max(0, (progress?.current_index || 1) - 1);
  state.examChoiceAnswers = {};
  for (const item of progress?.questions || []) {
    if (
      item.answered &&
      item.selected_option_index !== null &&
      item.selected_option_index !== undefined
    ) {
      state.examChoiceAnswers[item.question_id] = item.selected_option_index;
    }
  }
}

async function refreshExamProgress(currentQuestionId = null) {
  if (!state.examSession?.session_id || !state.accessToken) {
    return null;
  }
  const resolvedId = currentQuestionId || getCurrentExamQuestion()?.question_id;
  const base = `/api/exams/sessions/${state.examSession.session_id}/progress`;
  const url = resolvedId
    ? `${base}?current_question_id=${encodeURIComponent(resolvedId)}`
    : base;
  const progress = await fetchJson(url, { headers: authHeaders() });
  syncExamStateFromProgress(progress);
  return progress;
}

function formatExamCountLabel(count) {
  return `${Number(count || 0)} Frage${Number(count || 0) === 1 ? "" : "n"}`;
}

function formatExamDuration(seconds) {
  const total = Math.max(0, Number(seconds) || 0);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${mins}:${String(secs).padStart(2, "0")} Min`;
}

function examGradeFromPercent(percent) {
  const score = Number(percent) || 0;
  if (score >= 92) {
    return { note: "1", label: "Sehr gut" };
  }
  if (score >= 81) {
    return { note: "2", label: "Gut" };
  }
  if (score >= 67) {
    return { note: "3", label: "Befriedigend" };
  }
  if (score >= 50) {
    return { note: "4", label: "Ausreichend" };
  }
  if (score >= 30) {
    return { note: "5", label: "Mangelhaft" };
  }
  return { note: "6", label: "Ungenügend" };
}

function examResultSubtitle(result) {
  const score = Number(result?.score_percent) || 0;
  if (result?.passed) {
    if (score >= 90) {
      return "Hervorragende Leistung!";
    }
    if (score >= 75) {
      return "Sehr gute Leistung!";
    }
    return "Bestanden — weiter so!";
  }
  if (score >= 45) {
    return "Das war knapp! Kopf hoch.";
  }
  return "Dranbleiben — du schaffst das!";
}

function examWeakTopicLabel(result) {
  const weak = result?.weak_categories?.[0];
  if (!weak?.category_slug) {
    return "deine Schwachstellen";
  }
  return weak.category_slug.replace(/-/g, " ");
}

function persistExamResult(result) {
  state.examResult = result;
  try {
    sessionStorage.setItem("ol_exam_result", JSON.stringify(result));
  } catch {
    /* ignore storage errors */
  }
}

function loadExamResult() {
  if (state.examResult) {
    return state.examResult;
  }
  try {
    const raw = sessionStorage.getItem("ol_exam_result");
    state.examResult = raw ? JSON.parse(raw) : null;
  } catch {
    state.examResult = null;
  }
  return state.examResult;
}

function clearExamResult() {
  state.examResult = null;
  try {
    sessionStorage.removeItem("ol_exam_result");
  } catch {
    /* ignore storage errors */
  }
}

function bindExamResultScreens(root, config) {
  if (!["/pruefungen/bestanden", "/pruefungen/durchgefallen"].includes(config.path)) {
    return;
  }
  const result = loadExamResult();
  if (!result) {
    return;
  }
  const grade = examGradeFromPercent(result.score_percent);
  const xpTotal = liveNumber(state.dashboard?.xp ?? state.gamification?.xp, 0);
  const correct = Number(result.choice_correct) || 0;
  const wrong = Number(result.wrong_count) || 0;
  const open = Number(result.unanswered_count) || 0;
  const total = Number(result.choice_total) || correct + wrong + open;
  const scoreSummary = `${result.score_percent}% (${correct}/${total} richtig)`;
  const subtitle = examResultSubtitle(result);
  const encourage = `Wiederhole deine Schwachstellen in ${examWeakTopicLabel(result)} und lade dein Wissen vor dem nächsten Versuch auf.`;

  root.querySelectorAll("[data-bind='exam-result-xp-total']").forEach((el) => {
    el.textContent = `${Number(xpTotal).toLocaleString("de-DE")} XP`;
  });
  root.querySelectorAll("[data-bind='exam-result-subtitle']").forEach((el) => {
    el.textContent = subtitle;
  });
  root.querySelectorAll("[data-bind='exam-result-grade-note']").forEach((el) => {
    el.textContent = `Note ${grade.note}`;
  });
  root.querySelectorAll("[data-bind='exam-result-grade-label']").forEach((el) => {
    el.textContent = grade.label;
  });
  root.querySelectorAll("[data-bind='exam-result-score-summary']").forEach((el) => {
    el.textContent = scoreSummary;
  });
  root.querySelectorAll("[data-bind='exam-result-xp-awarded']").forEach((el) => {
    el.textContent = `+${Number(result.xp_awarded) || 0} XP`;
  });
  root.querySelectorAll("[data-bind='exam-result-correct-count']").forEach((el) => {
    el.textContent = formatExamCountLabel(correct);
  });
  root.querySelectorAll("[data-bind='exam-result-wrong-count']").forEach((el) => {
    el.textContent = formatExamCountLabel(wrong);
  });
  root.querySelectorAll("[data-bind='exam-result-open-count']").forEach((el) => {
    el.textContent = formatExamCountLabel(open);
  });
  root.querySelectorAll("[data-bind='exam-result-duration']").forEach((el) => {
    el.textContent = formatExamDuration(result.duration_seconds);
  });
  root.querySelectorAll("[data-bind='exam-result-correct-num']").forEach((el) => {
    el.textContent = String(correct);
  });
  root.querySelectorAll("[data-bind='exam-result-wrong-num']").forEach((el) => {
    el.textContent = String(wrong);
  });
  root.querySelectorAll("[data-bind='exam-result-open-num']").forEach((el) => {
    el.textContent = String(open);
  });
  root.querySelectorAll("[data-bind='exam-result-encourage']").forEach((el) => {
    el.textContent = encourage;
  });
  root.querySelectorAll("[data-bind='exam-result-record']").forEach((el) => {
    const showRecord = Boolean(result.passed && Number(result.score_percent) >= 75);
    el.hidden = !showRecord;
  });
}

function bindExamSharedFields(root, progress) {
  if (!progress) {
    return;
  }
  const timerText = formatExamTimer(state.examSession?.expires_at);
  root.querySelectorAll("[data-bind='exam-timer']").forEach((el) => {
    el.textContent = timerText;
  });
  root.querySelectorAll("[data-bind='exam-progress-label']").forEach((el) => {
    el.textContent = `${progress.current_index}/${progress.total_questions}`;
  });
  root.querySelectorAll("[data-bind='exam-title']").forEach((el) => {
    el.textContent = progress.exam_title || state.examSession?.exam?.title || "Prüfung";
  });
  root.querySelectorAll("[data-bind='exam-answered-count']").forEach((el) => {
    el.textContent = String(progress.answered_count);
  });
  root.querySelectorAll("[data-bind='exam-open-count']").forEach((el) => {
    el.textContent = String(progress.open_count);
  });
  root.querySelectorAll("[data-bind='exam-marked-count']").forEach((el) => {
    el.textContent = String(progress.marked_count);
  });
  root.querySelectorAll("[data-bind='exam-answered-summary']").forEach((el) => {
    el.textContent = formatExamCountLabel(progress.answered_count);
  });
  root.querySelectorAll("[data-bind='exam-open-summary']").forEach((el) => {
    el.textContent = formatExamCountLabel(progress.open_count);
  });
  root.querySelectorAll("[data-bind='exam-marked-summary']").forEach((el) => {
    el.textContent = formatExamCountLabel(progress.marked_count);
  });
  root.querySelectorAll("[data-bind='exam-progress-bar']").forEach((el) => {
    el.style.width = `${Math.max(0, Math.min(100, progress.progress_percent || 0))}%`;
  });
  root.querySelectorAll("[data-bind='exam-bg-question-label']").forEach((el) => {
    el.textContent = `Frage ${progress.current_index} von ${progress.total_questions}`;
  });
  root.querySelectorAll("[data-bind='exam-bg-question-prompt']").forEach((el) => {
    el.textContent = progress.current_prompt || "Keine Frage geladen.";
  });
}

function renderExamOverviewGrid(progress) {
  return (progress.questions || [])
    .map((item) => {
      const classes = ["ex-ov-cell"];
      if (item.is_current) {
        classes.push("current");
      } else if (item.answered) {
        classes.push("answered");
      } else {
        classes.push("open");
      }
      if (item.marked) {
        classes.push("marked");
      }
      return `<button type="button" class="${classes.join(" ")}" data-exam-action="goto-question" data-question-id="${item.question_id}" data-q-index="${item.index - 1}">${item.index}${item.marked ? "<i aria-hidden=\"true\"></i>" : ""}</button>`;
    })
    .join("");
}

function bindExamLiveScreens(root, config) {
  if (!state.examSession || !config.path?.startsWith("/pruefungen/")) {
    return;
  }
  const progress = state.examProgress;
  if (!progress) {
    return;
  }
  bindExamSharedFields(root, progress);
  if (config.path?.startsWith("/pruefungen/frage")) {
    const exam = state.examSession.exam;
    const current = getCurrentExamQuestion();
    if (!current) {
      return;
    }
    const promptEl = root.querySelector("[data-bind='exam-question-prompt']");
    if (promptEl) {
      promptEl.textContent = current.prompt;
    }
    root.querySelectorAll("[data-bind='exam-topic']").forEach((el) => {
      el.textContent = exam.title || "Prüfung";
    });
    root.querySelectorAll("[data-bind='exam-question-label']").forEach((el) => {
      el.textContent = `Frage ${progress.current_index}`;
    });
    const optionsRoot = root.querySelector("[data-bind='exam-options']");
    if (optionsRoot) {
      const letters = ["A", "B", "C", "D", "E", "F"];
      optionsRoot.innerHTML = current.options
        .map(
          (option, index) => `
          <button type="button" class="ex-q-opt${
            state.examChoiceAnswers[current.question_id] === index ? " selected" : ""
          }" data-exam-action="choice" data-question-id="${current.question_id}" data-index="${index}">
            <span>${letters[index] || index + 1}</span>
            <strong>${escapeHtml(option)}</strong>
          </button>`,
        )
        .join("");
    }
    const flagBtn = root.querySelector("[data-exam-action='toggle-mark']");
    if (flagBtn) {
      const marked = Boolean(
        progress.questions?.find((item) => item.question_id === current.question_id)?.marked,
      );
      flagBtn.classList.toggle("active", marked);
      flagBtn.setAttribute("aria-pressed", marked ? "true" : "false");
    }
    startExamTimer(root);
    return;
  }
  if (config.path === "/pruefungen/uebersicht") {
    const grid = root.querySelector("[data-bind='exam-overview-grid']");
    if (grid) {
      grid.innerHTML = renderExamOverviewGrid(progress);
    }
    startExamTimer(root);
    return;
  }
  if (config.path === "/pruefungen/timer") {
    const exam = state.examSession.exam;
    const current = getCurrentExamQuestion();
    bindExamSharedFields(root, progress);
    if (current) {
      const promptEl = root.querySelector("[data-bind='exam-question-prompt']");
      if (promptEl) {
        promptEl.textContent = current.prompt;
      }
      root.querySelectorAll("[data-bind='exam-topic']").forEach((el) => {
        el.textContent = exam.title || "Prüfung";
      });
      root.querySelectorAll("[data-bind='exam-question-label']").forEach((el) => {
        el.textContent = `Frage ${progress.current_index}`;
      });
      const optionsRoot = root.querySelector("[data-bind='exam-options']");
      if (optionsRoot) {
        const letters = ["A", "B", "C", "D", "E", "F"];
        optionsRoot.innerHTML = current.options
          .map(
            (option, index) => `
          <button type="button" class="ex-tm-opt${
            state.examChoiceAnswers[current.question_id] === index ? " selected" : ""
          }" data-exam-action="choice" data-question-id="${current.question_id}" data-index="${index}">
            <span>${letters[index] || index + 1}</span>
            <strong>${escapeHtml(option)}</strong>
          </button>`,
          )
          .join("");
      }
    }
    const warn = root.querySelector(".ex-tm-warn");
    if (warn && state.examSession.expires_at) {
      const remainingMs = new Date(state.examSession.expires_at).getTime() - Date.now();
      warn.hidden = remainingMs > 10 * 60 * 1000;
    }
    const marked = (progress.questions || []).filter((item) => item.marked).map((item) => `#${item.index}`);
    const jumpStrong = root.querySelector(".ex-tm-jump strong");
    if (jumpStrong) {
      jumpStrong.textContent = marked.length ? marked.join(", ") : "keine";
    }
    startExamTimer(root);
    return;
  }
  if (config.path === "/pruefungen/abgabe") {
    startExamTimer(root);
  }
}

function categorySlugToTitle(slug) {
  return String(slug || "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .trim();
}

function resolveCategoryTitle(slug) {
  const categories = state.chapter?.subchapters || [];
  const match = categories.find((item) => item.slug === slug);
  if (match?.title) {
    return match.title;
  }
  return categorySlugToTitle(slug);
}

function categoryDisplayTitle(slug) {
  const full = resolveCategoryTitle(slug);
  const parts = full.split(": ");
  return parts.length > 1 ? parts[parts.length - 1].trim() : full;
}

function weakTopicMeta(percent) {
  const score = Number(percent) || 0;
  if (score >= 90) {
    return { className: "perfect", label: "Perfekt", hint: "" };
  }
  if (score >= 70) {
    return { className: "ok", label: "OK", hint: "" };
  }
  if (score >= 55) {
    return { className: "fair", label: "Ausbaufähig", hint: "Empfehlung: Grundlagen auffrischen" };
  }
  if (score >= 40) {
    return { className: "weak", label: "Schwach", hint: "Empfehlung: Formeln wiederholen" };
  }
  return { className: "critical", label: "Kritisch", hint: "Empfehlung: Kapitel erneut durcharbeiten" };
}

function resolveWeakTopics() {
  const examResult = loadExamResult();
  const examTopics = examResult?.category_breakdown || examResult?.weak_categories;
  if (Array.isArray(examTopics) && examTopics.length) {
    return { source: "exam", topics: examTopics };
  }
  const dashboardTopics = state.dashboard?.weak_categories;
  if (Array.isArray(dashboardTopics) && dashboardTopics.length) {
    return {
      source: "dashboard",
      topics: dashboardTopics.map((item) => {
        const wrong = Number(item.wrong_count) || 0;
        const total = Number(item.total_count) || Math.max(wrong, 1);
        const correct = Math.max(total - wrong, 0);
        const percent = Number(item.percent) || Math.round((correct / total) * 100);
        return {
          category_slug: item.category_slug,
          wrong_count: wrong,
          total_count: total,
          correct_count: correct,
          percent,
        };
      }),
    };
  }
  return { source: "empty", topics: [] };
}

function renderWeakTopicCard(topic, index) {
  const title = categorySlugToTitle(topic.category_slug);
  const total = Number(topic.total_count) || Math.max(Number(topic.wrong_count) || 0, 1);
  const correct = Number(topic.correct_count);
  const resolvedCorrect = Number.isFinite(correct) ? correct : Math.max(total - (Number(topic.wrong_count) || 0), 0);
  const percent = Number(topic.percent) || Math.round((resolvedCorrect / total) * 100);
  const meta = weakTopicMeta(percent);
  const hint = meta.hint
    ? `<p>${escapeHtml(meta.hint)}</p>`
    : "";
  const actions =
    percent < 90
      ? `<div class="ex-wk-actions"><a href="/lernen/fragen/fehler" data-page-link>Thema üben</a><img src="/static/figma/exam/ex-wk-chev.svg" width="16" height="16" alt="" /></div>`
      : "";
  return `
    <article class="ex-wk-card ${meta.className}">
      <div class="ex-wk-top">
        <div class="ex-wk-title"><em>${index + 1}.</em><strong>${escapeHtml(title)}</strong></div>
        <span class="ex-wk-badge">${escapeHtml(meta.label)}</span>
      </div>
      <div class="ex-wk-bar">
        <div class="ex-wk-bar-track"><i style="width:${percent}%"></i></div>
        <span>${resolvedCorrect}/${total} (${percent}%)</span>
      </div>
      ${hint}
      ${actions}
    </article>`;
}

function bindExamWeakTopics(root, config) {
  if (config.path !== "/pruefungen/schwach") {
    return;
  }
  const { source, topics } = resolveWeakTopics();
  const xpTotal = liveNumber(state.dashboard?.xp ?? state.gamification?.xp, 0);
  root.querySelectorAll("[data-bind='exam-result-xp-total']").forEach((el) => {
    el.textContent = `${Number(xpTotal).toLocaleString("de-DE")} XP`;
  });
  root.querySelectorAll("[data-bind='weak-topics-sub']").forEach((el) => {
    el.textContent =
      source === "exam"
        ? "Basierend auf deiner letzten Prüfung:"
        : source === "dashboard"
          ? "Basierend auf deinem Lernstand:"
          : "Noch keine Schwachstellen erkannt.";
  });
  const back = root.querySelector("[data-bind='weak-back-link']");
  if (back) {
    const result = loadExamResult();
    back.setAttribute("href", result ? (result.passed ? "/pruefungen/bestanden" : "/pruefungen/durchgefallen") : "/pruefungen");
  }
  const list = root.querySelector("[data-bind='exam-weak-list']");
  if (!list) {
    return;
  }
  list.innerHTML = topics.length
    ? topics.map((topic, index) => renderWeakTopicCard(topic, index)).join("")
    : `<article class="ex-wk-card ok"><div class="ex-wk-top"><div class="ex-wk-title"><strong>Alles im grünen Bereich</strong></div></div><p>Starte eine Prüfung oder beantworte Fragen, um gezielte Empfehlungen zu erhalten.</p></article>`;
}

function examKindLabel(exam) {
  const id = String(exam?.exam_id || "");
  const checkpointMatch = id.match(/^checkpoint-(\d+)/);
  if (checkpointMatch) {
    const number = Number(checkpointMatch[1]);
    if (number === 12) {
      return "Zwischenprüfung";
    }
    if (number === 24) {
      return "Abschlussprüfung";
    }
    return number > 12 ? "Checkpoint Jahr 2" : "Checkpoint Jahr 1";
  }
  const title = String(exam?.title || "");
  if (/zwischen/i.test(title)) {
    return "Zwischenprüfung";
  }
  if (/abschluss/i.test(title) || /\bAP\b/.test(title)) {
    return "Abschlussprüfung";
  }
  return "Themenprüfung";
}

function checkpointNumber(exam) {
  const match = String(exam?.exam_id || "").match(/^checkpoint-(\d+)/);
  return match ? Number(match[1]) : 0;
}

function currentJourneyMonth() {
  const unlocked = (state.journey || []).filter((entry) => !entry.locked);
  if (!unlocked.length) {
    return Number(state.learnMonth) || 1;
  }
  return Math.max(...unlocked.map((entry) => Number(entry.month) || 1));
}

function featuredExam() {
  const exams = state.exams || [];
  const preferId = currentJourneyMonth() >= 13 ? "checkpoint-24" : "checkpoint-12";
  return (
    exams.find((exam) => exam.exam_id === preferId) ||
    exams.find((exam) => exam.is_checkpoint) ||
    exams[0]
  );
}

function curatedExamList(exams) {
  const wanted = [
    "checkpoint-12",
    "checkpoint-24",
    "exam-01",
    "checkpoint-13",
    "checkpoint-18",
    "checkpoint-22",
  ];
  const byId = Object.fromEntries(exams.map((exam) => [exam.exam_id, exam]));
  const picked = wanted.map((id) => byId[id]).filter(Boolean);
  if (picked.length) {
    return picked;
  }
  return exams.slice(0, 8);
}

function questionPracticeStatus(progress) {
  if (!progress || !Number(progress.answered_count)) {
    return "open";
  }
  if (progress.mastered) {
    return "done";
  }
  if (Number(progress.correct_streak) >= 1) {
    return "once";
  }
  return "wrong";
}

function practiceQuestionPool() {
  if (state.practiceMode === "unit") {
    return state.questions || [];
  }
  return state.allQuestions?.length ? state.allQuestions : state.questions || [];
}

function questionMonthNumber(question) {
  const cats = state.chapter?.subchapters || [];
  const cat = cats.find((item) => item.slug === question.category_slug);
  if (cat?.month) {
    return Number(cat.month);
  }
  const match = String(question.category_slug || "").match(/^m(\d{2})-/);
  return match ? Number(match[1]) : 0;
}

function filteredPracticeQuestions(filter = state.practiceFilter || "all") {
  return practiceQuestionPool().filter((question) => {
    const status = questionPracticeStatus(state.questionProgress?.[question.question_id]);
    return filter === "all" || status === filter;
  });
}

function renderPracticeQuestionList(root, config, questionList) {
  if (config.path === "/lernen/fragen/fehler" && !state.practiceFilter) {
    state.practiceFilter = "wrong";
  }
  const filter = state.practiceFilter || (config.path === "/lernen/fragen/fehler" ? "wrong" : "all");
  state.practiceFilter = filter;
  const source = filteredPracticeQuestions(filter);
  const dots = {
    done: "/static/figma/learn2/dot-green.svg",
    once: "/static/figma/learn2/dot-blue.svg",
    open: "/static/figma/learn2/dot-gray.svg",
    wrong: "/static/figma/learn2/dot-red.svg",
  };
  root.querySelectorAll("[data-practice-filter]").forEach((el) => {
    el.classList.toggle("active", el.dataset.practiceFilter === filter);
  });
  const total = practiceQuestionPool().length;
  const done = filteredPracticeQuestions("done").length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const stats = root.querySelector(".topic-stats .row-between strong, .figma-topic-stats .row-between strong");
  if (stats) {
    stats.textContent = `${source.length} von ${total} Fragen — ${done} abgeschlossen`;
  }
  const pctLabel = root.querySelector(".mastery-pct, .learn-pct-ring strong");
  if (pctLabel) {
    pctLabel.textContent = `${pct}%`;
  }
  const fill = root.querySelector(".mastery-fill");
  if (fill) {
    fill.style.width = `${pct}%`;
  }
  const months = new Map();
  source.forEach((question) => {
    const month = questionMonthNumber(question);
    if (!months.has(month)) {
      months.set(month, new Map());
    }
    const categories = months.get(month);
    const key = question.category_slug || "allgemein";
    if (!categories.has(key)) {
      categories.set(key, []);
    }
    categories.get(key).push(question);
  });
  const pool = practiceQuestionPool();
  const journeyByMonth = Object.fromEntries(
    (state.journey || []).map((entry) => [Number(entry.month), entry]),
  );
  questionList.innerHTML = source.length
    ? [...months.entries()]
        .map(([month, categories]) => {
          const monthTitle = journeyByMonth[month]?.title || `Monat ${month}`;
          const categoryBlocks = [...categories.entries()]
            .map(([slug, questions]) => {
              const title = categoryDisplayTitle(slug);
              const rows = questions
                .map((question) => {
                  const resolvedIndex = pool.findIndex((item) => item.question_id === question.question_id);
                  const status = questionPracticeStatus(state.questionProgress?.[question.question_id]);
                  return `
          <a class="q-row" href="/lernen/frage" data-page-link data-q-index="${Math.max(resolvedIndex, 0)}">
            <img class="q-dot" src="${dots[status] || dots.open}" width="10" height="10" alt="" />
            <span>${escapeHtml(question.prompt)}</span>
            <span class="q-status-label">${status === "done" ? "fertig" : status === "once" ? "1× richtig" : status === "wrong" ? "falsch" : "offen"}</span>
            <img class="q-chev" src="/static/figma/learn2/q-chevron.svg" width="14" height="14" alt="" />
          </a>`;
                })
                .join("");
              return `<div class="q-group"><p class="q-group-title">${escapeHtml(title)}</p>${rows}</div>`;
            })
            .join("");
          return `<div class="q-month"><p class="q-month-title">Monat ${month} · ${escapeHtml(monthTitle)}</p>${categoryBlocks}</div>`;
        })
        .join("")
    : `<p class="muted">Keine Fragen in diesem Filter.</p>`;
}

function bindExamHub(root, config) {
  if (!["/pruefungen", "/pruefungen/liste-legacy"].includes(config.path)) {
    return;
  }
  const exams = state.exams || [];
  const featured = featuredExam();
  root.querySelectorAll("[data-bind='exam-hero-title']").forEach((el) => {
    el.textContent = featured?.title || "IHK Zwischenprüfung";
  });
  const yearTwoCount = exams.filter((exam) => checkpointNumber(exam) >= 13).length;
  root.querySelectorAll("[data-bind='exam-hub-subtitle']").forEach((el) => {
    el.textContent = yearTwoCount
      ? `24 Monate · ${yearTwoCount} Checkpoints Jahr 2 plus ZP und AP`
      : "24 Monate · ZP, Checkpoints und Abschlussprüfung";
  });
  const icons = [
    "/static/figma/exam/ex-timer.svg",
    "/static/figma/exam/ex-settings.svg",
    "/static/figma/gx/clock.svg",
    "/static/figma/gx/star.svg",
  ];
  const colors = ["purple", "blue", "", ""];
  const kinds = [...new Set(exams.map((exam) => examKindLabel(exam)))];
  const chipHost = root.querySelector("[data-bind='exam-kind-chips']");
  if (chipHost) {
    const activeKind = state.examKindFilter || "alle";
    chipHost.innerHTML = ["Alle", ...kinds]
      .map((kind) => {
        const value = kind.toLowerCase();
        const on = activeKind === value || (kind === "Alle" && activeKind === "alle");
        return `<button type="button" class="gx-exam-chip${on ? " active" : ""}" data-action="exam-kind-filter" data-exam-kind="${escapeHtml(value)}">${escapeHtml(kind)}</button>`;
      })
      .join("");
  }
  const visibleExams = exams.filter((exam) => {
    const kind = examKindLabel(exam).toLowerCase();
    return !state.examKindFilter || state.examKindFilter === "alle" || kind === state.examKindFilter;
  });
  const simExams =
    !state.examKindFilter || state.examKindFilter === "alle"
      ? curatedExamList(visibleExams)
      : visibleExams;
  const simGrid = root.querySelector(".gx-sim-grid");
  if (simGrid) {
    simGrid.innerHTML = simExams.length
      ? simExams
          .map((exam, index) => {
            const count = exam.questions?.length || 0;
            const minutes = exam.time_limit_minutes || 0;
            return `
          <button class="gx-card gx-sim" type="button" data-action="exam-start-shortcut" data-exam-id="${escapeHtml(exam.exam_id)}">
            <img src="${icons[index % icons.length]}" width="24" height="24" alt="" />
            <strong>${escapeHtml(exam.title)}</strong>
            <span>${count} Fragen${minutes ? ` • ${minutes} Min` : ""}</span>
            <em${exam.is_checkpoint ? ' class="ok"' : ""}>${escapeHtml(examKindLabel(exam))}</em>
          </button>`;
          })
          .join("")
      : `<p class="muted">Keine Prüfungen in diesem Bereich.</p>`;
  }
  const featuredHost = root.querySelector("[data-bind='exam-list-live']");
  if (featuredHost) {
    featuredHost.innerHTML = exams.length
      ? exams
          .slice(0, 4)
          .map((exam, index) => {
            const count = exam.questions?.length || 0;
            const minutes = exam.time_limit_minutes || 0;
            const featured = index === 0 ? " featured" : "";
            return `
            <article class="ex-card${featured}">
              <div class="ex-card-top">
                <span class="ex-ico ${colors[index % colors.length] || "blue"}"><img src="${icons[index % icons.length]}" width="22" height="22" alt="" /></span>
                <div>
                  <strong>${escapeHtml(exam.title)}</strong>
                  <p>${count} Fragen${minutes ? ` — ${minutes} Minuten` : ""}</p>
                </div>
              </div>
              <div class="ex-divider" aria-hidden="true"></div>
              <div class="ex-card-bottom">
                <div class="ex-attempt">
                  <img src="/static/figma/exam/ex-alert.svg" width="14" height="14" alt="" />
                  <span>${exam.passing_score_percent}% Bestehensgrenze</span>
                </div>
                <button class="ex-start${index === 0 ? " purple" : ""}" type="button" data-action="exam-start-shortcut" data-exam-id="${escapeHtml(exam.exam_id)}">Starten</button>
              </div>
            </article>`;
          })
          .join("")
      : `<p class="muted">Keine Prüfungen geladen.</p>`;
  }
  const resultsRoot = root.querySelector(".gx-results") || root.querySelector("[data-bind='exam-results-live']");
  const last = loadExamResult();
  if (resultsRoot) {
    if (!last) {
      resultsRoot.innerHTML = `<p class="muted">Noch keine Prüfungsergebnisse.</p>`;
    } else {
      const href = last.passed ? "/pruefungen/bestanden" : "/pruefungen/durchgefallen";
      const cls = last.passed ? "ok" : "warn";
      resultsRoot.innerHTML = `
        <a class="gx-card gx-result" href="${href}" data-page-link>
          <div><strong>${escapeHtml(last.exam_title || "Prüfung")}</strong><span>Letzter Versuch</span></div>
          <div class="gx-score ${cls}">${last.score_percent}%<i></i></div>
        </a>
        <a class="gx-card gx-result" href="/pruefungen/schwach" data-page-link>
          <div><strong>Schwache Themen</strong><span>Auswertung</span></div>
          <div class="gx-score warn">Öffnen<i></i></div>
        </a>`;
    }
  }
}

function bindGxLearnScreen(root, config) {
  if (config.path !== "/lernen") {
    return;
  }
  const units = allLearnUnits();
  const unit = currentLearnUnit();
  const months = new Set(units.map((item) => Number(item.month) || 1));
  root.querySelectorAll("[data-bind='journey-month-title']").forEach((el) => {
    el.textContent = `${months.size || 24} Monate · ${units.length} Lerneinheiten`;
  });
  if (!unit) {
    return;
  }
  root.querySelectorAll("[data-bind='continue-title']").forEach((el) => {
    el.textContent = `Lernmodul: ${unit.title}`;
  });
  const recommend = root.querySelector(".gx-recommend");
  if (recommend) {
    recommend.dataset.unitSlug = unit.slug;
  }
}

async function ensureQuestionProgress() {
  if (!state.accessToken) {
    return;
  }
  const rows = await fetchJson("/api/progress", { headers: authHeaders() }).catch(() => []);
  state.questionProgress = Object.fromEntries(
    (rows || []).map((item) => [item.question_id, item]),
  );
}

async function startPracticeQuestions(filter = "all") {
  await requireAuth();
  state.practiceFilter = filter || "all";
  state.practiceMode = "all";
  await loadAllQuestions();
  await ensureQuestionProgress();
  await navigateTo("/lernen/fragen");
}

async function openLearnUnit(slug) {
  await requireAuth();
  const unit =
    (state.units || []).find((item) => item.slug === slug) || currentLearnUnit();
  if (!unit) {
    await startPracticeQuestions("all");
    return;
  }
  try {
    await loadUnitBySlug(unit.slug);
  } catch {
    state.activeUnit = unit;
  }
  await navigateTo("/lernen/einheit");
}

async function startLearnUnit(slug) {
  await requireAuth();
  const unit =
    (state.units || []).find((item) => item.slug === slug) || currentLearnUnit();
  if (!unit) {
    await startPracticeQuestions("all");
    return;
  }
  state.activeUnit = unit;
  state.practiceMode = "unit";
  const categorySlug = (unit.category_slugs || [])[0];
  const month = unit.month || state.learnMonth || 1;
  const questions = categorySlug
    ? await fetchJson(`/api/questions?category_slug=${encodeURIComponent(categorySlug)}`).catch(() => [])
    : await fetchJson(`/api/questions?month=${month}`).catch(() => []);
  if (questions.length) {
    state.questions = questions;
    state.currentQuestionIndex = 0;
  } else {
    await loadAllQuestions();
  }
  await navigateTo("/lernen/frage");
}

function bindLearnPractice(root, config) {
  if (config.path === "/lernen/fragen/fehler") {
    const banner = root.querySelector(".error-alert-banner p");
    if (banner) {
      const weak = state.dashboard?.weak_categories?.[0];
      const wrong = Number(state.dashboard?.wrong_answers) || 0;
      banner.textContent = weak
        ? `${wrong || weak.wrong_count} Fehler in ${categorySlugToTitle(weak.category_slug)} — Wiederholung empfohlen!`
        : wrong
          ? `${wrong} Fehler — Wiederholung empfohlen!`
          : "Noch keine Fehler gespeichert.";
    }
  }
  if (!["/lernen/feedback/richtig", "/lernen/feedback/falsch"].includes(config.path)) {
    return;
  }
  const attempt = state.lastAttempt;
  if (!attempt) {
    return;
  }
  const letters = ["A", "B", "C", "D", "E", "F"];
  const prompt = root.querySelector(".q-prompt");
  if (prompt) {
    prompt.textContent = attempt.prompt;
  }
  const answers = root.querySelector(".fb-answers");
  if (answers) {
    answers.innerHTML = (attempt.options || [])
      .map((option, index) => {
        const isCorrect = index === attempt.correct_option_index;
        const isSelectedWrong = index === attempt.selected_option_index && !attempt.is_correct;
        const cls = isCorrect ? "correct" : isSelectedWrong ? "wrong" : "dim";
        const mark = isCorrect
          ? `<img class="fb-mark" src="/static/figma/learn2/q-check-green.svg" width="18" height="18" alt="" />`
          : isSelectedWrong
            ? `<img class="fb-mark" src="/static/figma/learn2/q-x-red.svg" width="18" height="18" alt="" />`
            : "";
        return `<div class="fb-answer ${cls}"><span class="answer-letter">${letters[index] || index + 1}</span><span class="answer-text">${escapeHtml(option)}</span>${mark}</div>`;
      })
      .join("");
  }
  const explain = root.querySelector(".fb-explain p:not(.fb-label):not(.fb-correct-answer):not(.fb-explain-text)") ||
    root.querySelector(".fb-explain-text") ||
    root.querySelector(".fb-explain p:nth-of-type(2)");
  if (explain && attempt.explanation) {
    explain.textContent = attempt.explanation;
  }
  const correctLine = root.querySelector(".fb-correct-answer");
  if (correctLine && attempt.options) {
    const letter = letters[attempt.correct_option_index] || "";
    correctLine.textContent = `${letter}) ${attempt.options[attempt.correct_option_index] || ""}`;
  }
  const xpPill = root.querySelector(".xp-pill");
  if (xpPill) {
    xpPill.textContent = attempt.is_correct ? "+20 XP" : "+0 XP";
  }
  const topicPill = root.querySelector(".q-meta-row .topic-pill");
  if (topicPill) {
    topicPill.textContent = categoryDisplayTitle(attempt.category_slug || "Fachkunde");
  }
  root.querySelectorAll(".q-tracker, .ld-counter").forEach((el) => {
    if (state.questions.length) {
      el.textContent = `${state.currentQuestionIndex + 1}/${state.questions.length}`;
    }
  });
  const fill = root.querySelector(".q-progress-fill");
  if (fill && state.questions.length) {
    fill.style.width = `${Math.round(((state.currentQuestionIndex + 1) / state.questions.length) * 100)}%`;
  }
}

function bindFachkundeScreens(root, config) {
  if (!config.path?.startsWith("/fachkunde")) {
    return;
  }
  const units = state.units || [];
  const done = units.filter((unit) => unit.completed).length;
  const total = units.length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  if (config.path === "/fachkunde") {
    const introText = root.querySelector(".fk-intro-prog-text strong");
    if (introText) {
      introText.textContent = `${done} von ${total || 0} Lerneinheiten`;
    }
    const introBar = root.querySelector(".fk-intro-bar i");
    if (introBar) {
      introBar.style.width = `${pct}%`;
    }
    const grid = root.querySelector(".fk-grid2");
    if (grid && units.length) {
      const icons = [
        "fk-settings.svg",
        "fk-diamond.svg",
        "fk-ruler.svg",
        "fk-wind.svg",
        "fk-droplets.svg",
        "fk-cpu.svg",
      ];
      grid.innerHTML = units
        .slice(0, 24)
        .map((unit, index) => {
          const status = unit.completed ? "ok" : "info";
          const label = unit.completed ? "✓ Fertig" : "Offen";
          const unitPct = unit.completed ? 100 : 0;
          return `
            <a class="fk-card" href="/fachkunde/einheit" data-page-link data-unit-slug="${escapeHtml(unit.slug)}">
              <div class="fk-card-top">
                <span class="fk-ico ${unit.completed ? "green" : "blue"}"><img src="/static/figma/fk/${icons[index % icons.length]}" width="18" height="18" alt="" /></span>
                <span class="fk-status ${status}">${label}</span>
              </div>
              <strong>${escapeHtml(unit.title)}</strong>
              <div class="fk-card-prog"><span>Monat ${unit.month}</span><b>${unitPct}%</b></div>
              <div class="fk-mini"><i class="${unit.completed ? "green" : ""}" style="width:${unitPct}%"></i></div>
            </a>`;
        })
        .join("");
    }
  }
  const unit = state.activeUnit || units[0];
  if (!unit) {
    return;
  }
  if (config.path === "/fachkunde/einheit") {
    const kicker = root.querySelector(".fk-eu-kicker");
    if (kicker) {
      kicker.textContent = `Lerneinheit ${unit.position || 1} · Monat ${unit.month}`;
    }
    const headTitle = root.querySelector(".fk-eu-head-center strong");
    if (headTitle) {
      headTitle.textContent = unit.title;
    }
    const leadH = root.querySelector(".fk-eu-lead h2");
    if (leadH) {
      leadH.textContent = unit.title;
    }
    const leadP = root.querySelector(".fk-eu-lead p");
    if (leadP) {
      leadP.textContent = unit.subtitle || unit.practice_task || "Theorie & Praxis";
    }
    const sectionH = root.querySelector(".fk-eu-section h3");
    const sectionP = root.querySelector(".fk-eu-section p");
    const block = unit.theory_blocks?.[0];
    if (sectionH && block) {
      sectionH.textContent = block.heading;
    }
    if (sectionP && block) {
      sectionP.textContent = block.body;
    }
    const merke = root.querySelector(".fk-eu-merke p");
    if (merke && block?.key_points?.[0]) {
      merke.textContent = `Merke: ${block.key_points[0]}`;
    }
  }
  if (config.path === "/fachkunde/abschluss") {
    const head = root.querySelector(".fk-ac-head-title");
    if (head) {
      head.textContent = unit.title;
    }
    const heroP = root.querySelector(".fk-ac-hero-text p");
    if (heroP) {
      heroP.textContent = unit.subtitle || unit.title;
    }
  }
  bindFachkundeExercises(root, config.path || "");
}

function bindProgressScreens(root, config) {
  const weekMinutes = Array.isArray(state.dashboard?.week_minutes)
    ? state.dashboard.week_minutes
    : [0, 0, 0, 0, 0, 0, 0];
  const weekMax = Math.max(...weekMinutes, 1);
  const weekLetters = ["M", "D", "M", "D", "F", "S", "S"];
  const gxWeek = root.querySelector(".gx-week-bars");
  if (gxWeek) {
    gxWeek.innerHTML = weekLetters
      .map((label, index) => {
        const mins = Number(weekMinutes[index]) || 0;
        const height = mins ? Math.max(8, Math.round((mins / weekMax) * 80)) : 4;
        const muted = mins ? "" : " muted";
        return `<div class="gx-wbar${muted}"><i style="height:${height}px"></i><span>${label}</span></div>`;
      })
      .join("");
  }
  if (!["/fortschritt/pruefungsreife", "/fortschritt/ausstehend"].includes(config.path)) {
    return;
  }
  const readiness = Number(state.dashboard?.readiness_percent) || 0;
  root.querySelectorAll(".fp-pr-ring strong, .fp-pr-score-info p").forEach((el) => {
    if (el.matches(".fp-pr-ring strong")) {
      el.textContent = `${readiness}%`;
    }
  });
  const badge = root.querySelector(".fp-pr-badge");
  if (badge) {
    badge.textContent = readiness >= 80 ? "Prüfungsreif" : "Noch nicht prüfungsreif";
    badge.classList.toggle("warn", readiness < 80);
    badge.classList.toggle("ok", readiness >= 80);
  }
  const list = root.querySelector(".fp-pr-list");
  if (!list) {
    return;
  }
  const months = (state.journey || []).slice(0, 8);
  if (!months.length) {
    return;
  }
  list.innerHTML = months
    .map((month) => {
      const total = Number(month.total_categories) || 0;
      const done = Number(month.completed_categories) || 0;
      const pct = total ? Math.round((done / total) * 100) : 0;
      const cls = month.locked ? "locked" : pct >= 80 ? "ok" : pct >= 40 ? "warn" : "bad";
      const icon = month.locked
        ? "fp-pr-lock.svg"
        : pct >= 80
          ? "fp-pr-check.svg"
          : pct >= 40
            ? "fp-pr-alert.svg"
            : "fp-pr-x.svg";
      return `
        <article class="fp-pr-item ${cls}">
          <img src="/static/figma/fp/${icon}" width="20" height="20" alt="" />
          <div class="fp-pr-item-body">
            <div class="fp-pr-item-top"><strong>${escapeHtml(month.title || `Monat ${month.month}`)}</strong><em>${pct}%</em></div>
            <div class="fp-pr-item-bar"><i style="width:${pct}%"></i></div>
          </div>
        </article>`;
    })
    .join("");
}

function persistLevelUp(payload) {
  state.levelUp = payload;
  try {
    sessionStorage.setItem("ol_level_up", JSON.stringify(payload));
  } catch {
    /* ignore storage errors */
  }
}

function loadLevelUp() {
  if (state.levelUp) {
    return state.levelUp;
  }
  try {
    const raw = sessionStorage.getItem("ol_level_up");
    state.levelUp = raw ? JSON.parse(raw) : null;
  } catch {
    state.levelUp = null;
  }
  return state.levelUp;
}

function clearLevelUp() {
  state.levelUp = null;
  try {
    sessionStorage.removeItem("ol_level_up");
  } catch {
    /* ignore storage errors */
  }
}

function bindLevelUpScreen(root, config) {
  if (config.path !== "/level-up") {
    return;
  }
  const payload = loadLevelUp();
  if (!payload) {
    return;
  }
  const level = Number(payload.to) || Number(state.dashboard?.level) || 1;
  const title = levelTitleFor(level);
  const xp = liveNumber(state.dashboard?.xp ?? state.gamification?.xp, 0);
  const xpPer = liveNumber(state.dashboard?.xp_per_level ?? state.gamification?.xp_per_level, 120);
  const xpInto = liveNumber(state.dashboard?.xp_into_level ?? state.gamification?.xp_into_level, xp % xpPer);
  const remaining = Math.max(xpPer - xpInto, 0);
  const badges = state.gamification?.badges || state.dashboard?.badges || [];
  const latestBadge = badges[badges.length - 1];
  root.querySelectorAll("[data-bind='level-up-num']").forEach((el) => {
    el.textContent = String(level);
  });
  root.querySelectorAll("[data-bind='level-up-summary']").forEach((el) => {
    el.textContent = `Level ${level} erreicht · Neuer Titel: ${title}`;
  });
  const rewards = root.querySelector("[data-bind='level-up-rewards']");
  if (rewards) {
    const items = [`+${Number(payload.bonus_xp) || 100} Bonus-XP`];
    if (latestBadge) {
      items.push(`Neues Abzeichen: ${latestBadge}`);
    }
    if (payload.unlock_title) {
      items.push(`Freischaltung: ${payload.unlock_title}`);
    }
    rewards.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }
  root.querySelectorAll("[data-bind='level-up-next']").forEach((el) => {
    el.textContent =
      remaining > 0
        ? `Level ${level + 1} in ${Number(remaining).toLocaleString("de-DE")} XP`
        : "Maximales Level erreicht";
  });
  root.querySelectorAll("[data-bind='level-up-continue']").forEach((el) => {
    el.setAttribute("href", payload.returnTo || "/dashboard");
  });
}

async function bindLandingStats() {
  if (!state.contentStats) {
    state.contentStats = await fetchJson("/api/content/stats").catch(() => null);
  }
  const stats = state.contentStats;
  if (!stats) {
    return;
  }
  document.querySelectorAll("[data-bind='stat-questions']").forEach((el) => {
    el.textContent = Number(stats.quiz_questions || 0).toLocaleString("de-DE");
  });
  document.querySelectorAll("[data-bind='stat-units']").forEach((el) => {
    el.textContent = Number(stats.learning_units || 0).toLocaleString("de-DE");
  });
  document.querySelectorAll("[data-bind='stat-exams']").forEach((el) => {
    el.textContent = Number(stats.exams || 0).toLocaleString("de-DE");
  });
  document.querySelectorAll("[data-bind='landing-preview-unit']").forEach((el) => {
    el.textContent = stats.preview_unit_title || "Lerneinheit";
  });
}

const LEARN_CONTINUE = "__learn_continue__";

function maybeQueueLevelUp(previousLevel, returnTo = "/dashboard", nextLevel = null) {
  const prev = Number(previousLevel) || 0;
  const next = Number(nextLevel ?? state.dashboard?.level ?? state.gamification?.level) || prev;
  if (next <= prev) {
    return false;
  }
  const unlockTitle = state.dashboard?.continue_title || state.dashboard?.review_topic || "";
  persistLevelUp({
    from: prev,
    to: next,
    bonus_xp: 100,
    unlock_title: unlockTitle,
    returnTo,
  });
  return true;
}

function applyAppearance(prefs = state.preferences) {
  const theme = prefs?.theme || localStorage.getItem("ol_theme") || "light";
  const language = prefs?.language || state.selectedLanguage || localStorage.getItem("ol_language") || "de";
  const high = Boolean(prefs?.high_contrast ?? localStorage.getItem("ol_high_contrast") === "1");
  const reduce = Boolean(prefs?.reduce_motion ?? localStorage.getItem("ol_reduce_motion") === "1");
  const root = document.documentElement;
  if (theme === "system") {
    root.dataset.theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    root.dataset.themePref = "system";
  } else {
    root.dataset.theme = theme === "dark" ? "dark" : "light";
    delete root.dataset.themePref;
  }
  root.lang = language;
  root.classList.toggle("high-contrast", high);
  root.classList.toggle("reduce-motion", reduce);
  localStorage.setItem("ol_theme", theme);
  localStorage.setItem("ol_language", language);
  localStorage.setItem("ol_high_contrast", high ? "1" : "0");
  localStorage.setItem("ol_reduce_motion", reduce ? "1" : "0");
  state.selectedLanguage = language;
  if (prefs) {
    state.preferences = { ...prefs, theme, language, high_contrast: high, reduce_motion: reduce };
  }
}

function bindAuthScreens(root, config) {
  if (config.path === "/sprache") {
    const activeLang = state.preferences?.language || state.selectedLanguage || "de";
    state.selectedLanguage = activeLang;
    const cohortInput = root.querySelector('input[name="cohort"]');
    if (cohortInput && state.preferences?.cohort_code) {
      cohortInput.value = state.preferences.cohort_code;
    }
    root.querySelectorAll(".lang-row[data-lang]").forEach((row) => {
      const selected = row.dataset.lang === activeLang;
      row.classList.toggle("active", selected);
      row.setAttribute("aria-selected", selected ? "true" : "false");
      const check = row.querySelector(".lang-check");
      const radio = row.querySelector(".lang-radio");
      if (check) {
        check.hidden = !selected;
      }
      if (radio) {
        radio.hidden = selected;
      }
    });
  }
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
  state.examProgress = null;
  state.examChoiceAnswers = {};
  state.examOpenAnswers = {};
  clearExamResult();
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
  const timerElement =
    root.querySelector("[data-bind='exam-timer']") ||
    root.querySelector("#exam-timer") ||
    root.querySelector(".ex-q-timer strong") ||
    root.querySelector(".ex-tm-timer strong");
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
  state.currentExamQuestionIndex = 0;
  await refreshExamProgress();
  await navigateTo("/pruefungen/frage", false);
}

async function gotoExamQuestion(questionId, questionIndex) {
  if (questionId) {
    state.currentExamQuestionIndex = questionIndex ?? state.currentExamQuestionIndex;
    await refreshExamProgress(questionId);
  }
  await navigateTo("/pruefungen/frage", false);
}

async function gotoNextExamQuestion() {
  const progress = state.examProgress;
  const questions = progress?.questions || [];
  const currentIndex = Math.max(0, (progress?.current_index || 1) - 1);
  const next = questions[currentIndex + 1];
  if (next) {
    await gotoExamQuestion(next.question_id, next.index - 1);
    return;
  }
  await navigateTo("/pruefungen/abgabe", false);
}

async function gotoPreviousExamQuestion() {
  const progress = state.examProgress;
  const questions = progress?.questions || [];
  const currentIndex = Math.max(0, (progress?.current_index || 1) - 1);
  const previous = questions[currentIndex - 1];
  if (previous) {
    await gotoExamQuestion(previous.question_id, previous.index - 1);
    return;
  }
  await navigateTo("/pruefungen/uebersicht", false);
}

async function toggleExamMark(questionId) {
  if (!state.examSession?.session_id) {
    return;
  }
  const resolvedId = questionId || getCurrentExamQuestion()?.question_id;
  if (!resolvedId) {
    return;
  }
  await fetchJson(`/api/exams/sessions/${state.examSession.session_id}/marks`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ question_id: resolvedId }),
  });
  await refreshExamProgress(resolvedId);
  await navigateTo(window.location.pathname, false);
}

async function startExamShortcut(examId) {
  await requireAuth();
  if (!state.exams.length) {
    showToast("Keine Pruefungen geladen.");
    return;
  }
  const resolvedId =
    examId ||
    EXAM_SHORTCUT_IDS.zp ||
    state.exams.find((exam) => /ZP-SIM|Zwischenpr/i.test(exam.title))?.exam_id;
  const exam = state.exams.find((item) => item.exam_id === resolvedId) || state.exams[0];
  if (!exam) {
    showToast("Pruefung nicht gefunden.");
    return;
  }
  state.activeExam = exam;
  await startExamSession();
  showToast(`${exam.title} gestartet`);
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
  await refreshExamProgress(questionId);
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
  const prevLevel = Number(state.dashboard?.level ?? state.gamification?.level) || 0;
  const result = await fetchJson(
    `/api/exams/sessions/${state.examSession.session_id}/submit`,
    { method: "POST", headers: authHeaders() },
  );
  state.examSession = null;
  persistExamResult(result);
  await refreshPrivateData();
  const returnTo = result.passed ? "/pruefungen/bestanden" : "/pruefungen/durchgefallen";
  if (maybeQueueLevelUp(prevLevel, returnTo)) {
    await navigateTo("/level-up");
    return;
  }
  await navigateTo(returnTo);
}

async function bindPlatformTools(root, config) {
  const path = config?.path || window.location.pathname;
  if (path.startsWith("/fachkunde/toleranz") || path.startsWith("/fachkunde/spritz") || path.startsWith("/fachkunde/messschieber")) {
    bindFachkundeExercises(root, path);
  }
  if (!state.accessToken) {
    applyAppearance();
    return;
  }
  try {
    if (path.startsWith("/lernen/formeltrainer") || path.startsWith("/lernen/flashcard")) {
      state.formulas = await fetchJson("/api/formulas");
      renderFormulas(root, state.formulas);
    }
    if (path.startsWith("/lernen/fehlerdiagnose")) {
      state.diagnosisCases = await fetchJson("/api/diagnosis", { headers: authHeaders() });
      renderDiagnosis(root, state.diagnosisCases);
    }
    if (path.startsWith("/lernen/video")) {
      state.videos = await fetchJson("/api/videos", { headers: authHeaders() });
      renderVideos(root, state.videos);
    }
    if (path.startsWith("/lernen/uebersetzung") || path.startsWith("/lernen/glossar")) {
      if (path.startsWith("/lernen/uebersetzung")) {
        await renderTranslationOverlay(root);
      }
      const input = root.querySelector("[data-action='glossary-search']");
      const query = input?.value || "";
      const terms = await fetchJson(query ? `/api/glossary?q=${encodeURIComponent(query)}` : "/api/glossary");
      renderGlossary(root, terms);
      if (input && !input.dataset.bound) {
        input.dataset.bound = "1";
        let timer = 0;
        input.addEventListener("input", () => {
          window.clearTimeout(timer);
          timer = window.setTimeout(async () => {
            const next = await fetchJson(
              input.value ? `/api/glossary?q=${encodeURIComponent(input.value)}` : "/api/glossary",
            );
            renderGlossary(root, next);
          }, 200);
        });
      }
    }
    if (path.startsWith("/lernen/flashcard")) {
      if (!state.formulas.length) {
        state.formulas = await fetchJson("/api/formulas");
      }
      renderFlashcard(root, state.formulas);
    }
    if (path.startsWith("/mehr/darstellung")) {
      bindAppearanceScreen(root);
    }
    if (path.startsWith("/mehr/benachrichtigungen") || path === "/notifications") {
      state.notifications = await fetchJson("/api/notifications", { headers: authHeaders() }).catch(() => []);
      if (!state.notificationSettings) {
        state.notificationSettings = await fetchJson("/api/me/notifications/settings", {
          headers: authHeaders(),
        });
      }
      bindNotificationScreen(root);
    }
    if (path.startsWith("/mehr/coach") || path.startsWith("/mehr/lernplan")) {
      if (!state.coachPlan) {
        state.coachPlan = await fetchJson("/api/coach/plan", { headers: authHeaders() }).catch(() => null);
      }
      bindCoachScreens(root, path);
    }
    if (path.startsWith("/berichtsheft")) {
      bindReportScreens(root, path);
    }
    if (path.startsWith("/ausbilder") && STAFF_ROLES.has(state.role)) {
      const output = root.querySelector("[data-bind='trainer-output']");
      if (output && !output.innerHTML.trim()) {
        const [risk, reports] = await Promise.all([
          fetchJson("/api/trainer/risk", { headers: authHeaders() }).catch(() => []),
          fetchJson("/api/trainer/reports", { headers: authHeaders() }).catch(() => []),
        ]);
        output.innerHTML = `
          <p>${risk.length} Teilnehmende im Risiko-Radar.</p>
          <ul>${risk
            .slice(0, 8)
            .map(
              (row) =>
                `<li>${escapeHtml(row.alias)} · ${row.readiness_percent}% · Risiko ${escapeHtml(row.risk)}</li>`,
            )
            .join("")}</ul>
          <p>${reports.length} Berichtsheft-Eintraege.</p>`;
      }
    }
    if (path.startsWith("/admin") && state.role === "admin") {
      const output = root.querySelector("[data-bind='trainer-output']");
      if (output && !output.innerHTML.trim()) {
        const monitoring = await fetchJson("/api/admin/monitoring", { headers: authHeaders() });
        output.innerHTML = `<p>Nutzer ${monitoring.learners} · Fragen ${monitoring.quiz_questions} · Einheiten ${monitoring.learning_units} · offene Reviews ${monitoring.pending_reviews}</p>`;
      }
    }
  } catch (error) {
    showToast(error.message);
  }
}

function renderFormulas(root, formulas) {
  const scroll = root.querySelector(".formel-scroll");
  if (!scroll || !formulas.length) {
    return;
  }
  const chips = scroll.querySelector(".formel-chips");
  const topics = ["alle", ...new Set(formulas.map((item) => item.topic))];
  if (chips) {
    chips.innerHTML = topics
      .map(
        (topic, index) =>
          `<button type="button" class="formel-chip${index === 0 ? " active" : ""}" data-action="filter-formulas" data-topic="${escapeHtml(topic)}">${escapeHtml(topic)}</button>`,
      )
      .join("");
  }
  const cards = formulas
    .map((formula, index) => {
      if (index === 0) {
        const legend = (formula.legend || [])
          .map((item) => `<div><b>${escapeHtml(item.symbol)}</b><span>${escapeHtml(item.meaning)}</span></div>`)
          .join("");
        return `<article class="formel-card expanded">
          <div class="formel-card-head"><div><strong>${escapeHtml(formula.title)}</strong><p>${escapeHtml(formula.topic)}</p></div></div>
          <div class="formel-box">${escapeHtml(formula.expression)}</div>
          <div class="formel-legend">${legend}</div>
          <div class="formel-example"><p class="formel-example-label">Beispiel:</p><p>${escapeHtml(formula.example)}</p></div>
          <div class="formel-card-foot">
            <span class="formel-diff">${escapeHtml(formula.difficulty)}</span>
            <button type="button" class="formel-practice" data-action="practice-formula" data-slug="${escapeHtml(formula.slug)}">Ueben <span>+10 XP</span></button>
          </div>
        </article>`;
      }
      return `<button type="button" class="formel-card collapsed" data-action="practice-formula" data-slug="${escapeHtml(formula.slug)}">
        <div class="formel-card-left"><strong>${escapeHtml(formula.title)}</strong><span class="formel-eq">${escapeHtml(formula.expression)}</span></div>
        <div class="formel-card-right"><span class="formel-diff">${escapeHtml(formula.difficulty)}</span></div>
      </button>`;
    })
    .join("");
  const chipHtml = chips ? chips.outerHTML : "";
  scroll.innerHTML = `${chipHtml}${cards}<p class="formel-all-btn">${formulas.length} Formeln geladen</p>`;
}

function renderGlossary(root, terms) {
  const host = root.querySelector("[data-bind='glossary-live']");
  if (!host) {
    return;
  }
  const grouped = new Map();
  (terms || []).forEach((item) => {
    const key = item.term || item.translation;
    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    grouped.get(key).push(item);
  });
  host.innerHTML = grouped.size
    ? [...grouped.entries()]
        .map(([term, rows]) => {
          const definition = rows.find((row) => row.definition)?.definition || rows[0].translation;
          const langs = rows
            .map((row) => `${row.language.toUpperCase()}: ${row.translation}`)
            .join(" · ");
          return `<article class="gx-card gx-glossar-item">
            <strong>${escapeHtml(term)}</strong>
            <p>${escapeHtml(definition)}</p>
            <span class="muted">${escapeHtml(langs)}</span>
          </article>`;
        })
        .join("")
    : `<p class="muted">Keine Begriffe gefunden.</p>`;
}

function renderFlashcard(root, formulas) {
  const host = root.querySelector("[data-bind='flashcard-live']");
  if (!host || !formulas.length) {
    return;
  }
  const currentSlug = state.activeFormulaSlug || formulas[0].slug;
  const index = Math.max(0, formulas.findIndex((item) => item.slug === currentSlug));
  const formula = formulas[index] || formulas[0];
  state.activeFormulaSlug = formula.slug;
  const legend = (formula.legend || [])
    .map((item) => `<div><b>${escapeHtml(item.symbol)}</b><span>${escapeHtml(item.meaning)}</span></div>`)
    .join("");
  host.innerHTML = `
    <article class="gx-card">
      <p class="gx-kicker">${escapeHtml(formula.topic)} · ${escapeHtml(formula.difficulty)}</p>
      <strong>${escapeHtml(formula.title)}</strong>
      <p class="gx-formula">${escapeHtml(formula.expression)}</p>
      <div class="gx-legend">${legend}</div>
      <p>${escapeHtml(formula.example)}</p>
    </article>
    <div class="gx-chips">
      <button class="gx-chip" type="button" data-action="practice-formula" data-slug="${escapeHtml(formula.slug)}">Geprüft (+10 XP)</button>
      <button class="gx-chip" type="button" data-action="next-formula">Nächste Formel</button>
      <a class="gx-chip" href="/lernen/formeltrainer" data-page-link>Alle Formeln</a>
    </div>`;
}

function renderDiagnosis(root, cases) {
  const list = root.querySelector(".fd-cases");
  if (!list || !cases.length) {
    return;
  }
  const colors = ["blue", "green", "red", "muted"];
  const solvedCount = cases.filter((item) => item.solved).length;
  list.innerHTML = cases
    .map((item, index) => {
      const color = colors[index % colors.length];
      const open = state.activeDiagnosisSlug === item.slug && !item.solved;
      const options = (item.options || [])
        .map(
          (option, optionIndex) =>
            `<button type="button" class="fd-option" data-action="solve-diagnosis" data-slug="${escapeHtml(item.slug)}" data-index="${optionIndex}">${escapeHtml(option)}</button>`,
        )
        .join("");
      const action = item.solved
        ? `<button type="button" class="fd-again" data-action="open-diagnosis" data-slug="${escapeHtml(item.slug)}">Nochmal</button>`
        : `<button type="button" class="fd-start ${color}" data-action="open-diagnosis" data-slug="${escapeHtml(item.slug)}">Starten</button>`;
      return `<article class="fd-case ${color}${item.solved ? " solved" : ""}">
        <div class="fd-case-body">
          <div class="fd-case-head"><div><p class="fd-cat">${escapeHtml(item.topic)}</p><strong>${escapeHtml(item.title)}</strong></div></div>
          <p>${escapeHtml(item.symptom)}</p>
          ${open ? `<div class="fd-options">${options}</div>` : ""}
          ${item.solved && item.explanation ? `<p class="fd-explain">${escapeHtml(item.explanation)}</p>` : ""}
          <div class="fd-case-meta ${item.solved ? "solved" : ""}">
            <span>${item.solved ? "Gelöst" : `${escapeHtml(item.difficulty)} · ${item.estimated_minutes} Min`}</span>
            ${action}
          </div>
        </div>
      </article>`;
    })
    .join("");
  const progress = root.querySelector(".fd-prog-text");
  if (progress) {
    const pct = cases.length ? Math.round((solvedCount / cases.length) * 100) : 0;
    progress.innerHTML = `<span>${solvedCount} von ${cases.length} Szenarien gelöst</span><strong>${pct}%</strong>`;
    const bar = root.querySelector(".fd-prog-bar i");
    if (bar) {
      bar.style.width = `${pct}%`;
    }
  }
}

function formatVideoTime(seconds) {
  const total = Math.max(0, Math.round(Number(seconds) || 0));
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function renderVideos(root, videos) {
  if (!videos.length) {
    return;
  }
  const current =
    videos.find((item) => item.slug === state.activeVideoSlug) || videos[0];
  state.activeVideoSlug = current.slug;
  const title = root.querySelector(".vid-title, .vid-player-meta strong");
  if (title) {
    title.textContent = current.title;
  }
  const instructor = root.querySelector(".vid-instructor strong");
  if (instructor) {
    instructor.textContent = current.instructor;
  }
  const durationEls = root.querySelectorAll(".vid-player-meta span, .vid-pill.time");
  durationEls.forEach((el) => {
    el.textContent = `${formatVideoTime(current.duration_seconds)} Min`.replace(" Min Min", " Min");
  });
  const play = root.querySelector(".vid-play-btn");
  if (play) {
    play.dataset.action = "watch-video";
    play.dataset.slug = current.slug;
    play.dataset.toast = "";
  }
  const timeline = root.querySelector(".vid-timeline i");
  if (timeline) {
    const pct = current.duration_seconds
      ? Math.min(100, Math.round((current.watched_seconds / current.duration_seconds) * 100))
      : 0;
    timeline.style.width = `${pct}%`;
  }
  const chapters = root.querySelector(".vid-chapter-list");
  if (chapters) {
    chapters.innerHTML = (current.chapters || [])
      .map((chapter) => {
        const done = current.watched_seconds >= chapter.start_seconds;
        const active =
          current.watched_seconds >= chapter.start_seconds &&
          current.watched_seconds < chapter.start_seconds + 90;
        return `<button type="button" class="vid-chapter${done ? " done" : ""}${active ? " active" : ""}" data-action="seek-video" data-slug="${escapeHtml(current.slug)}" data-seconds="${chapter.start_seconds}">
          <div class="vid-chapter-left"><span class="t">${formatVideoTime(chapter.start_seconds)}</span><span class="n">${escapeHtml(chapter.title)}</span></div>
        </button>`;
      })
      .join("");
  }
  const next = root.querySelector(".vid-next strong");
  if (next && current.next_slug) {
    const upcoming = videos.find((item) => item.slug === current.next_slug);
    if (upcoming) {
      next.textContent = upcoming.title;
    }
    const link = root.querySelector(".vid-next");
    if (link) {
      link.dataset.action = "open-video";
      link.dataset.slug = current.next_slug;
    }
  }
}

function bindAppearanceScreen(root) {
  const prefs = state.preferences || {};
  const theme = prefs.theme || "light";
  root.querySelectorAll("[data-action='set-theme']").forEach((btn) => {
    btn.classList.toggle("on", btn.dataset.theme === theme);
  });
  root.querySelectorAll("[data-action='toggle-pref']").forEach((btn) => {
    const on = Boolean(prefs[btn.dataset.pref]);
    btn.classList.toggle("on", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  });
}

function setNotificationToggle(btn, on) {
  btn.classList.toggle("on", on);
  btn.setAttribute("aria-pressed", on ? "true" : "false");
  const img = btn.querySelector("img");
  if (img) {
    img.src = on ? "/static/figma/mehr/bn-toggle-on.svg" : "/static/figma/mehr/bn-toggle-off.svg";
  }
}

function bindNotificationScreen(root) {
  const settings = state.notificationSettings || {};
  root.querySelectorAll("[data-action='toggle-notification']").forEach((btn) => {
    setNotificationToggle(btn, Boolean(settings[btn.dataset.setting]));
  });
}

function coachTime() {
  return new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

function ensureCoachMessages() {
  if (state.coachMessages.length) {
    return;
  }
  const greeting =
    state.coachPlan?.greeting ||
    "Hallo! Ich kann Fragen erklären, Formeln ableiten oder deinen Lernplan optimieren.";
  state.coachMessages = [{ role: "ai", text: greeting, time: coachTime() }];
}

function renderCoachChat(root) {
  const host = root.querySelector(".kc-chat");
  if (!host) {
    return;
  }
  ensureCoachMessages();
  host.innerHTML = state.coachMessages
    .map((item) => {
      const href = item.href
        ? `<p><a href="${escapeHtml(item.href)}" data-page-link>Öffnen</a></p>`
        : "";
      return `<div class="kc-msg ${item.role === "me" ? "me" : "ai"}">
        <div class="kc-bubble">${escapeHtml(item.text).replace(/\n/g, "<br>")}${href}</div>
        <time>${escapeHtml(item.time || "")}</time>
      </div>`;
    })
    .join("");
  host.scrollTop = host.scrollHeight;
}

function bindCoachScreens(root, path) {
  if (path.startsWith("/mehr/coach")) {
    renderCoachChat(root);
  }
  if (path.startsWith("/mehr/lernplan")) {
    const plan = state.coachPlan;
    if (!plan) {
      return;
    }
    const goal = root.querySelector(".lp-goal-head strong");
    if (goal) {
      goal.textContent = `Ziel: Monat ${plan.focus_month} abschließen`;
    }
    const rings = root.querySelectorAll(".lp-ring b");
    if (rings[0]) {
      rings[0].textContent = `${plan.readiness_percent}%`;
    }
    const week = root.querySelector(".lp-week-card");
    if (week) {
      const days = ["Mo", "Di", "Mi", "Do", "Fr"];
      const tips = plan.tips || [];
      week.querySelectorAll(".lp-day").forEach((row, index) => {
        const tip = tips[index % Math.max(tips.length, 1)];
        const title = row.querySelector("strong");
        const meta = row.querySelector("span");
        if (title && tip) {
          title.textContent = tip.title;
        }
        if (meta) {
          meta.textContent = `${days[index] || ""} • 25 Min`;
        }
      });
    }
  }
}

async function bindReportScreens(root, path) {
  if (path === "/berichtsheft/ki") {
    try {
      state.reportSuggest = await fetchJson("/api/training-reports/suggest", {
        headers: authHeaders(),
      });
    } catch {
      state.reportSuggest = null;
    }
    const box = root.querySelector(".bh-ki-suggest-box");
    if (box && state.reportSuggest?.activities) {
      box.textContent = state.reportSuggest.activities;
    }
  }
  if (path === "/berichtsheft/neu" && state.reportSuggest?.activities) {
    const hidden = root.querySelector("textarea[name='activities']");
    const first = root.querySelector("textarea[name='mon']");
    if (hidden && !hidden.value) {
      hidden.value = state.reportSuggest.activities;
    }
    if (first && !first.value) {
      first.value = state.reportSuggest.activities;
    }
  }
  if (path === "/berichtsheft/unterschrift") {
    const report =
      (state.trainingReports || []).find((item) => item.status === "draft") ||
      (state.trainingReports || [])[0];
    const title = root.querySelector(".bh-sig-card-head strong");
    const hours = root.querySelector(".bh-sig-card-head em");
    const days = root.querySelector(".bh-sig-days");
    if (report && title) {
      title.textContent = `Bericht ${report.report_date}`;
    }
    if (report && hours) {
      hours.textContent = `${report.hours} Stunden`;
    }
    if (report && days) {
      days.innerHTML = `<div><b>Eintrag</b><span>${escapeHtml(report.activities)}</span></div>`;
    }
  }
}

const ISO_IT = { 6: 0.016, 7: 0.025, 8: 0.039 };
const ISO_FUND = {
  H: { es: (it) => it, ei: () => 0 },
  f: { es: () => -0.025, ei: (it) => -0.025 - it },
  g: { es: () => -0.009, ei: (it) => -0.009 - it },
};

function parseIsoClass(label) {
  const match = String(label || "").trim().match(/^([A-Za-z])(\d+)$/);
  if (!match) {
    return null;
  }
  return { letter: match[1], grade: Number(match[2]) };
}

function isoDeviations(label) {
  const parsed = parseIsoClass(label);
  if (!parsed) {
    return { es: 0.025, ei: 0 };
  }
  const it = ISO_IT[parsed.grade] || 0.025;
  const fund = ISO_FUND[parsed.letter] || ISO_FUND.H;
  return { es: fund.es(it), ei: fund.ei(it), it };
}

function formatMm(value) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(3)} mm`;
}

function updateToleranceCard(root) {
  const isoBtn = root.querySelector(".fk-tz-iso button.active") || root.querySelector(".fk-tz-iso button");
  const iso = isoBtn?.dataset.iso || "H7";
  const nominal = Number(root.querySelector("[data-tz-nominal]")?.textContent || "50") || 50;
  const { es, ei } = isoDeviations(iso);
  const limits = root.querySelectorAll(".fk-tz-limit");
  if (limits[0]) {
    limits[0].textContent = formatMm(es);
  }
  if (limits[1]) {
    limits[1].textContent = formatMm(ei);
  }
  const badge = root.querySelector(".fk-tz-badge strong");
  if (badge) {
    badge.textContent = `${nominal} ${iso}`;
  }
  const span = root.querySelector(".fk-tz-badge span");
  if (span) {
    span.textContent = `Toleranz: ${Math.abs(es - ei).toFixed(3)} mm`;
  }
  const measures = root.querySelector(".fk-tz-measures div");
  if (measures) {
    measures.innerHTML = `<span>Go: ${(nominal + ei).toFixed(3)} mm</span><span>NoGo: ${(nominal + es).toFixed(3)} mm</span>`;
  }
}

const SG_PHASES = [
  { title: "Werkzeug schließen", time: "t: 2.5s", desc: "Die Werkzeughälften fahren zusammen. Zuhaltekraft verhindert Aufspritzen.", p1: "Schließkraft: 800 kN", p2: "Schließgeschwindigkeit: 250 mm/s" },
  { title: "Einspritzen", time: "t: 1.8s", desc: "Die Schnecke fördert die Schmelze unter hohem Druck in die Kavität.", p1: "Einspritzdruck: 900 bar", p2: "Einspritzgeschwindigkeit: 80 mm/s" },
  { title: "Nachdrücken", time: "t: 4.0s", desc: "Nachdruck gleicht Schwindung aus, bis der Anguss erstarrt.", p1: "Nachdruck: 450 bar", p2: "Nachdruckzeit: 4 s" },
  { title: "Kühlen", time: "t: 18s", desc: "Das Formteil erstarrt. Kühlzeit bestimmt oft die Zykluszeit.", p1: "Werkzeugtemperatur: 40 °C", p2: "Kühlzeit: 18 s" },
  { title: "Auswerfen", time: "t: 2.2s", desc: "Das Werkzeug öffnet, Auswerfer stossen das Teil aus.", p1: "Öffnungsweg: 120 mm", p2: "Auswerferhub: 25 mm" },
];

function renderInjectionPhase(root, index) {
  const phase = SG_PHASES[index] || SG_PHASES[0];
  state.injectionPhase = index;
  root.querySelectorAll(".fk-sg-step").forEach((el, i) => {
    el.classList.toggle("active", i === index);
  });
  const title = root.querySelector(".fk-sg-detail-title strong");
  const num = root.querySelector(".fk-sg-detail-title em");
  const time = root.querySelector(".fk-sg-time");
  const desc = root.querySelector(".fk-sg-desc");
  const params = root.querySelectorAll(".fk-sg-params b");
  if (num) {
    num.textContent = String(index + 1);
  }
  if (title) {
    title.textContent = phase.title;
  }
  if (time) {
    time.textContent = phase.time;
  }
  if (desc) {
    desc.textContent = phase.desc;
  }
  if (params[0]) {
    params[0].textContent = phase.p1.split(": ")[1] || phase.p1;
  }
  if (params[1]) {
    params[1].textContent = phase.p2.split(": ")[1] || phase.p2;
  }
}

function bindFachkundeExercises(root, path) {
  if (path.startsWith("/fachkunde/toleranz")) {
    updateToleranceCard(root);
  }
  if (path.startsWith("/fachkunde/spritzguss")) {
    renderInjectionPhase(root, state.injectionPhase || 0);
  }
}

async function renderTranslationOverlay(root) {
  const question = state.questions[state.currentQuestionIndex];
  const prompt = question?.prompt || root.querySelector(".q-overlay-prompt")?.textContent || "";
  let terms = [];
  try {
    terms = await fetchJson("/api/glossary");
  } catch {
    terms = [];
  }
  const match =
    terms.find((item) => prompt.toLowerCase().includes(String(item.term || "").toLowerCase())) ||
    terms.find((item) => item.term === "Doppeltwirkender Zylinder") ||
    terms[0];
  if (!match) {
    return;
  }
  const grouped = terms.filter((item) => item.term === match.term);
  const de = root.querySelector(".term-de");
  if (de) {
    de.textContent = match.term;
  }
  const explain = root.querySelector(".explain-box p:last-child");
  if (explain) {
    explain.textContent = match.definition || "";
  }
  const flags = { en: "🇬🇧 English", tr: "🇹🇷 Türkçe", ar: "🇦🇪 العربية", uk: "🇺🇦 Українська", pl: "🇵🇱 Polski" };
  const rows = root.querySelector(".lang-rows");
  if (rows) {
    rows.innerHTML = grouped
      .map((item) => {
        const label = flags[item.language] || item.language.toUpperCase();
        return `<div><span>${label}</span><strong>${escapeHtml(item.translation)}</strong></div>`;
      })
      .join("");
  }
  root.dataset.term = match.term;
  root.dataset.speak = grouped.find((item) => item.language === (state.selectedLanguage || "de"))?.translation || match.term;
}

async function completeActiveLearnUnit() {
  const unit =
    state.activeUnit ||
    (state.units || []).find((item) =>
      (item.category_slugs || []).includes(state.questions[0]?.category_slug),
    );
  if (!unit?.slug || !state.accessToken) {
    return;
  }
  try {
    await fetchJson(`/api/learning/units/${encodeURIComponent(unit.slug)}/complete`, {
      method: "POST",
      headers: authHeaders(),
    });
    state.units = (state.units || []).map((item) =>
      item.slug === unit.slug ? { ...item, completed: true } : item,
    );
    state.activeUnit = { ...unit, completed: true };
  } catch {
    /* unit stays open if the server rejects completion */
  }
}

async function goToNextLearnStep(retry = false) {
  if (!state.questions.length) {
    await navigateTo("/lernen");
    return;
  }
  if (!retry) {
    if (state.practiceMode === "unit") {
      const next = Number(state.currentQuestionIndex) + 1;
      if (next >= state.questions.length) {
        await completeActiveLearnUnit();
        showToast("Lerneinheit abgeschlossen!");
        await loadAllUnits();
        state.currentQuestionIndex = 0;
        await navigateTo("/lernen");
        return;
      }
      state.currentQuestionIndex = next;
    } else {
      const current = state.questions[state.currentQuestionIndex];
      const pool = filteredPracticeQuestions();
      const pos = pool.findIndex((question) => question.question_id === current?.question_id);
      const nextItem = pos >= 0 ? pool[pos + 1] : pool[0];
      if (!nextItem || nextItem.question_id === current?.question_id) {
        showToast("Alle Fragen in diesem Filter durchgearbeitet!");
        state.currentQuestionIndex = 0;
        await navigateTo("/lernen/fragen");
        return;
      }
      const full = practiceQuestionPool();
      const nextIndex = full.findIndex((question) => question.question_id === nextItem.question_id);
      state.currentQuestionIndex = Math.max(0, nextIndex);
      state.questions = full;
    }
  }
  await navigateTo("/lernen/frage");
}

async function advanceLearnQuestion(retry = false) {
  if (!retry && loadLevelUp()) {
    persistLevelUp({ ...loadLevelUp(), returnTo: LEARN_CONTINUE });
    await navigateTo("/level-up");
    return;
  }
  await goToNextLearnStep(retry);
}

async function answerQuestion(index) {
  await requireAuth();
  const question = state.questions[state.currentQuestionIndex % state.questions.length];
  if (!question) {
    throw new Error("Keine Frage geladen.");
  }
  const prevLevel = Number(state.dashboard?.level ?? state.gamification?.level) || 1;
  const result = await fetchJson("/api/progress/attempt", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      question_id: question.question_id,
      selected_option_index: index,
    }),
  });
  state.lastAttempt = {
    ...result,
    prompt: question.prompt,
    options: question.options,
    category_slug: question.category_slug,
    selected_option_index: index,
  };
  if (state.dashboard) {
    if (result.level != null) {
      state.dashboard.level = result.level;
    }
    if (result.xp != null) {
      state.dashboard.xp = result.xp;
    }
  }
  if (result.leveled_up || Number(result.level) > prevLevel) {
    maybeQueueLevelUp(prevLevel, LEARN_CONTINUE, result.level);
  }
  state.questionProgress = state.questionProgress || {};
  state.questionProgress[result.question_id] = {
    question_id: result.question_id,
    answered_count: result.answered_count,
    wrong_count: result.wrong_count,
    correct_streak: result.correct_streak,
    mastered: result.mastered,
  };
  void refreshPrivateData().catch(() => null);
  await navigateTo(result.is_correct ? "/lernen/feedback/richtig" : "/lernen/feedback/falsch");
}

async function saveTrainingReport(formElement, status = "draft") {
  await requireAuth();
  const form = new FormData(formElement);
  const days = ["mon", "tue", "wed", "thu", "fri"]
    .map((name) => String(form.get(name) || "").trim())
    .filter(Boolean);
  const activities = (days.join(" ") || String(form.get("activities") || "")).trim();
  if (activities.length < 10) {
    throw new Error("Taetigkeiten muessen mindestens 10 Zeichen haben.");
  }
  const hours = Number(form.get("hours") || 8);
  await fetchJson("/api/training-reports", {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      report_date: String(form.get("report_date") || new Date().toISOString().slice(0, 10)),
      activities,
      hours,
      status,
    }),
  });
  await refreshPrivateData();
  showToast(status === "submitted" ? "Bericht eingereicht" : "Berichtsheft-Eintrag gespeichert");
  await navigateTo(status === "submitted" ? "/berichtsheft/unterschrift" : "/berichtsheft");
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
  syncAuthProfile({ ...state.authProfile, requires_password_change: false });
  await navigateTo("/sprache");
}

async function saveLanguagePreference() {
  await requireAuth();
  const language = state.selectedLanguage || "de";
  state.preferences = await fetchJson("/api/me/preferences", {
    method: "PUT",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ language }),
  });
  applyAppearance(state.preferences);
  showToast("Sprache gespeichert");
  if (state.authProfile?.onboarding_completed) {
    await navigateTo("/mehr");
    return;
  }
  await navigateTo("/onboarding");
}

async function completeOnboardingFlow() {
  await requireAuth();
  await recordConsent(true);
  await fetchJson("/api/auth/onboarding/complete", {
    method: "POST",
    headers: authHeaders(),
  });
  syncAuthProfile({
    ...state.authProfile,
    onboarding_completed: true,
    privacy_consent_accepted: true,
  });
  showToast("Willkommen im Lerncampus!");
  await navigateTo("/dashboard");
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
  if (layout === "login" || layout === "auth" || layout === "app" || layout === "landing") {
    document.documentElement.dataset.theme = "light";
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
    mainTabs.hidden = chrome === "campus" || chrome === "tablet" || chrome === "q-play" || chrome === "learn-drill" || chrome === "q-overlay" || chrome === "formel" || chrome === "ld" || chrome === "fk" || chrome === "exam" || chrome === "fp" || chrome === "bh" || chrome === "mehr" || chrome === "gx" || chrome === "ov";
  }
  if (campusTabs) {
    campusTabs.hidden = chrome !== "campus";
  }
  if (learnTabs) {
    learnTabs.hidden = chrome !== "learn-drill";
  }
  if (levelPill) {
    levelPill.hidden = chrome === "campus" || chrome === "tablet" || chrome === "learn-drill" || chrome === "q-play" || chrome === "q-overlay" || chrome === "formel" || chrome === "ld" || chrome === "fk" || chrome === "exam" || chrome === "fp" || chrome === "bh" || chrome === "mehr" || chrome === "gx" || chrome === "ov";
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
      (tab === "progress" && view === "progress") ||
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
  if (window.location.pathname !== resolved.pathname) {
    if (pushState && !routeConfig[pathname]?.aliasOf) {
      window.history.pushState({}, "", resolved.pathname);
    } else {
      window.history.replaceState({}, "", resolved.pathname);
    }
  }
  state.currentPath = resolved.pathname;
  if (["/passwort", "/sprache", "/onboarding"].includes(resolved.pathname) && !state.accessToken) {
    await navigateTo("/login", false);
    return;
  }
  if (["/passwort", "/sprache", "/onboarding"].includes(resolved.pathname) && state.accessToken) {
    try {
      const profile = await fetchJson("/api/auth/me", { headers: authHeaders() });
      syncAuthProfile(profile);
    } catch (error) {
      clearSession();
      await navigateTo("/login", false);
      return;
    }
  }
  if (state.accessToken) {
    if (resolved.pathname === "/passwort" && !state.authProfile.requires_password_change) {
      await navigateTo(resolvePostLoginRoute(), false);
      return;
    }
    if (
      resolved.pathname === "/sprache" &&
      state.authProfile.onboarding_completed &&
      state.authProfile.privacy_consent_accepted
    ) {
      await navigateTo("/dashboard", false);
      return;
    }
    if (resolved.pathname === "/onboarding" && state.authProfile.privacy_consent_accepted) {
      await navigateTo("/dashboard", false);
      return;
    }
  }
  if (["/pruefungen/bestanden", "/pruefungen/durchgefallen"].includes(resolved.pathname)) {
    if (!loadExamResult()) {
      showToast("Kein Prüfungsergebnis vorhanden.");
      await navigateTo("/pruefungen", false);
      return;
    }
  }
  if (resolved.pathname === "/level-up" && !loadLevelUp()) {
    await navigateTo("/dashboard", false);
    return;
  }
  if (resolved.pathname === "/" || config.layout === "landing") {
    await bindLandingStats();
  }
  if (resolved.pathname === "/dashboard" || resolved.pathname.startsWith("/dashboard/")) {
    if (state.accessToken) {
      state.dashboard = await fetchJson("/api/dashboard", { headers: authHeaders() }).catch(
        () => state.dashboard,
      );
    }
  }
  if (resolved.pathname.startsWith("/fachkunde")) {
    const unitHeaders = state.accessToken ? authHeaders() : {};
    state.units = await fetchJson("/api/learning/units", { headers: unitHeaders }).catch(
      () => state.units || [],
    );
  }
  if (["/lernen/fragen", "/lernen/fragen/fehler"].includes(resolved.pathname)) {
    state.practiceMode = "all";
    if (!state.allQuestions?.length) {
      await loadAllQuestions();
    } else {
      state.questions = state.allQuestions;
    }
    await ensureQuestionProgress();
  }
  if (["/lernen/frage", "/lernen/detail"].includes(resolved.pathname)) {
    if (state.practiceMode === "all") {
      if (!state.allQuestions?.length) {
        await loadAllQuestions();
      } else {
        state.questions = state.allQuestions;
      }
    } else if (!state.questions.length) {
      await loadAllQuestions();
    }
    await ensureQuestionProgress();
  }
  if (["/lernen/feedback/richtig", "/lernen/feedback/falsch"].includes(resolved.pathname)) {
    if (!state.questions.length) {
      await loadAllQuestions();
    }
  }
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
    ["/lernen", "/lernen/lernpfad", "/dashboard", "/lernen/einheit"].includes(resolved.pathname)
  ) {
    await loadAllUnits();
    if (state.accessToken) {
      state.journey = await fetchJson("/api/learning/journey", { headers: authHeaders() }).catch(
        () => state.journey,
      );
    }
  }
  if (
    ["/lernen/einheit", "/fachkunde/einheit", "/fachkunde/bausteine"].includes(resolved.pathname)
  ) {
    if (!state.activeUnit && state.units[0]) {
      await loadUnitBySlug(state.units[0].slug).catch(() => null);
    }
  }
  if (
    ["/fachkunde/lernpfad", "/ausbilder/planung"].includes(resolved.pathname)
  ) {
    await loadCurriculumBundle();
  }
  if (
    [
      "/gamification",
      "/gamification/xp",
      "/gamification/badges",
      "/gamification/streaks",
      "/fortschritt",
      "/fortschritt/xp",
      "/pruefungen",
      "/mehr",
    ].includes(resolved.pathname) &&
    state.accessToken
  ) {
    const [dashboard, journey, gamification] = await Promise.all([
      fetchJson("/api/dashboard", { headers: authHeaders() }).catch(() => state.dashboard),
      fetchJson("/api/learning/journey", { headers: authHeaders() }).catch(() => state.journey),
      fetchJson("/api/gamification", { headers: authHeaders() }).catch(() => state.gamification),
    ]);
    state.dashboard = dashboard;
    state.journey = journey;
    state.gamification = gamification;
    if (resolved.pathname === "/pruefungen") {
      await ensureQuestionProgress();
    }
  }
  if (["/mehr/coach", "/mehr/lernplan"].includes(resolved.pathname) && state.accessToken) {
    state.coachPlan = await fetchJson("/api/coach/plan", { headers: authHeaders() }).catch(
      () => state.coachPlan,
    );
  }
  const examLivePaths = [
    "/pruefungen/frage",
    "/pruefungen/uebersicht",
    "/pruefungen/abgabe",
    "/pruefungen/timer",
  ];
  if (examLivePaths.includes(resolved.pathname)) {
    if (!state.examSession?.session_id) {
      showToast("Keine aktive Prüfungssession.");
      if (resolved.pathname !== "/pruefungen") {
        await navigateTo("/pruefungen", false);
      }
      return;
    }
    try {
      await refreshExamProgress(getCurrentExamQuestion()?.question_id);
    } catch (error) {
      showToast(error.message);
      resetExamAttempt();
      if (resolved.pathname !== "/pruefungen") {
        await navigateTo("/pruefungen", false);
      }
      return;
    }
  }
  updateChrome(config, resolved.pathname);
  renderScreen(config);
}

async function loadAllUnits() {
  const unitHeaders = state.accessToken ? authHeaders() : {};
  state.units = await fetchJson("/api/learning/units", { headers: unitHeaders }).catch(
    () => state.units || [],
  );
}

async function loadAllQuestions() {
  const [questions, categories] = await Promise.all([
    fetchJson("/api/questions"),
    fetchJson("/api/questions/categories"),
  ]);
  state.allQuestions = questions;
  state.questions = questions;
  state.chapter = {
    title: "Alle Fragen",
    subchapters: categories,
  };
}

async function loadLearnMonth(month, { resetIndex = false } = {}) {
  const monthChanged = state.learnMonth !== month;
  state.learnMonth = month;
  if (resetIndex || monthChanged || !state.questions.length) {
    state.currentQuestionIndex = 0;
  }
  const unitHeaders = state.accessToken ? authHeaders() : {};
  const [units, questions, categories] = await Promise.all([
    fetchJson(`/api/learning/units?month=${month}`, { headers: unitHeaders }),
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
  await loadAllUnits();
  state.exams = await fetchJson("/api/exams");
  state.activeExam =
    state.exams.find((exam) => exam.exam_id === EXAM_SHORTCUT_IDS.diag) || state.exams[0] || null;
  await loadCurriculumBundle();
  state.contentStats = await fetchJson("/api/content/stats").catch(() => null);
  loadExamResult();
  loadLevelUp();
  if (state.accessToken) {
    try {
      await refreshPrivateData();
    } catch (error) {
      clearSession();
    }
  } else {
    applyAppearance();
  }
  await navigateTo(window.location.pathname, false);
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("a, button, [data-action]");
  if (!target) {
    return;
  }
  try {
    if (target.dataset.action === "filter-formulas") {
      event.preventDefault();
      const topic = target.dataset.topic === "alle" ? "" : target.dataset.topic;
      state.formulas = await fetchJson(topic ? `/api/formulas?topic=${encodeURIComponent(topic)}` : "/api/formulas");
      renderFormulas(document.getElementById("screen-root") || document, state.formulas);
      return;
    }
    if (target.dataset.action === "practice-formula") {
      event.preventDefault();
      await requireAuth();
      await fetchJson(`/api/formulas/${target.dataset.slug}/practice`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ correct: true }),
      });
      await refreshPrivateData();
      showToast("Formel geuebt. +XP");
      return;
    }
    if (target.dataset.action === "solve-diagnosis") {
      event.preventDefault();
      await requireAuth();
      const result = await fetchJson(`/api/diagnosis/${target.dataset.slug}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ selected_option_index: Number(target.dataset.index || 0) }),
      });
      showToast(result.is_correct ? "Richtig diagnostiziert" : result.explanation);
      state.activeDiagnosisSlug = null;
      state.diagnosisCases = await fetchJson("/api/diagnosis", { headers: authHeaders() });
      renderDiagnosis(document.getElementById("screen-root") || document, state.diagnosisCases);
      return;
    }
    if (target.dataset.action === "open-diagnosis") {
      event.preventDefault();
      state.activeDiagnosisSlug = target.dataset.slug;
      renderDiagnosis(document.getElementById("screen-root") || document, state.diagnosisCases);
      return;
    }
    if (target.dataset.action === "watch-video" || target.dataset.action === "seek-video" || target.dataset.action === "open-video") {
      event.preventDefault();
      await requireAuth();
      const slug = target.dataset.slug || state.activeVideoSlug;
      if (!slug) {
        return;
      }
      state.activeVideoSlug = slug;
      if (target.dataset.action === "open-video") {
        state.videos = await fetchJson("/api/videos", { headers: authHeaders() });
        renderVideos(document.getElementById("screen-root") || document, state.videos);
      }
      const video = (state.videos || []).find((item) => item.slug === slug);
      const duration = video?.duration_seconds || 120;
      const watched =
        target.dataset.action === "seek-video"
          ? Number(target.dataset.seconds || 0)
          : Math.min(duration, (video?.watched_seconds || 0) + 30);
      const completed = watched >= duration - 5;
      await fetchJson(`/api/videos/${slug}/progress`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ watched_seconds: watched, completed }),
      });
      state.videos = await fetchJson("/api/videos", { headers: authHeaders() });
      renderVideos(document.getElementById("screen-root") || document, state.videos);
      showToast(completed ? "Videolektion abgeschlossen" : "Videofortschritt gespeichert");
      return;
    }
    if (target.dataset.action === "speak-translation") {
      event.preventDefault();
      const root = document.getElementById("screen-root") || document;
      const text = root.dataset.speak || root.querySelector(".term-de")?.textContent || "";
      if (window.speechSynthesis && text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = state.selectedLanguage === "en" ? "en-GB" : "de-DE";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      }
      showToast("Aussprache");
      return;
    }
    if (target.dataset.action === "bookmark-term") {
      event.preventDefault();
      const root = document.getElementById("screen-root") || document;
      const term = root.dataset.term || root.querySelector(".term-de")?.textContent;
      if (term) {
        const bookmarks = JSON.parse(localStorage.getItem("ol_bookmarks") || "[]");
        if (!bookmarks.includes(term)) {
          bookmarks.push(term);
          localStorage.setItem("ol_bookmarks", JSON.stringify(bookmarks));
        }
      }
      showToast("Zur Merkliste hinzugefügt");
      await navigateTo("/dashboard/merksaetze");
      return;
    }
    if (target.dataset.action === "set-theme") {
      event.preventDefault();
      await requireAuth();
      state.preferences = await fetchJson("/api/me/preferences", {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ theme: target.dataset.theme }),
      });
      applyAppearance(state.preferences);
      bindAppearanceScreen(document.getElementById("screen-root") || document);
      showToast("Darstellung gespeichert");
      return;
    }
    if (target.dataset.action === "toggle-pref") {
      event.preventDefault();
      await requireAuth();
      const key = target.dataset.pref;
      const next = target.getAttribute("aria-pressed") !== "true";
      state.preferences = await fetchJson("/api/me/preferences", {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ [key]: next }),
      });
      applyAppearance(state.preferences);
      bindAppearanceScreen(document.getElementById("screen-root") || document);
      showToast("Einstellung gespeichert");
      return;
    }
    if (target.dataset.action === "toggle-notification") {
      event.preventDefault();
      await requireAuth();
      const key = target.dataset.setting;
      const next = target.getAttribute("aria-pressed") !== "true";
      state.notificationSettings = await fetchJson("/api/me/notifications/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ [key]: next }),
      });
      bindNotificationScreen(document.getElementById("screen-root") || document);
      showToast("Benachrichtigung gespeichert");
      return;
    }
    if (target.dataset.action === "coach-send" || target.dataset.action === "coach-chip") {
      event.preventDefault();
      await requireAuth();
      const input = document.querySelector("[data-coach-input]");
      const message =
        target.dataset.action === "coach-chip"
          ? target.dataset.message
          : String(input?.value || "").trim();
      if (!message) {
        return;
      }
      if (input) {
        input.value = "";
      }
      ensureCoachMessages();
      state.coachMessages.push({ role: "me", text: message, time: coachTime() });
      const reply = await fetchJson("/api/coach/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ message }),
      });
      state.coachMessages.push({
        role: "ai",
        text: reply.reply,
        href: reply.href,
        time: coachTime(),
      });
      if (window.location.pathname.startsWith("/mehr/coach")) {
        renderCoachChat(document.getElementById("screen-root") || document);
      } else if (reply.href) {
        await navigateTo(reply.href);
      }
      return;
    }
    if (target.dataset.action === "coach-attach") {
      event.preventDefault();
      showToast("Anhänge folgen in einer späteren Version. Schreibe deine Frage als Text.");
      return;
    }
    if (target.dataset.action === "apply-report-suggest") {
      event.preventDefault();
      await requireAuth();
      const draft =
        state.reportSuggest ||
        (await fetchJson("/api/training-reports/suggest", { headers: authHeaders() }));
      state.reportSuggest = draft;
      showToast("Vorschlag übernommen");
      await navigateTo("/berichtsheft/neu");
      return;
    }
    if (target.dataset.action === "dismiss-report-suggest") {
      event.preventDefault();
      state.reportSuggest = null;
      showToast("Vorschlag verworfen");
      await navigateTo("/berichtsheft/neu");
      return;
    }
    if (target.dataset.action === "save-report-draft") {
      event.preventDefault();
      const form = target.closest("form") || document.querySelector("form[data-action='create-report']");
      if (form) {
        await saveTrainingReport(form, "draft");
      }
      return;
    }
    if (target.dataset.action === "sign-report") {
      event.preventDefault();
      await requireAuth();
      const checkbox = document.querySelector(".bh-sig-check input");
      if (checkbox && !checkbox.checked) {
        showToast("Bitte die Richtigkeit bestätigen");
        return;
      }
      const reports = state.trainingReports.length
        ? state.trainingReports
        : await fetchJson("/api/training-reports", { headers: authHeaders() });
      const draft = reports.find((row) => row.status === "draft") || reports[0];
      if (!draft) {
        showToast("Kein Eintrag zum Unterschreiben");
        return;
      }
      await fetchJson(`/api/training-reports/${draft.id}/sign`, {
        method: "POST",
        headers: authHeaders(),
      });
      await refreshPrivateData();
      showToast("Zur Unterschrift eingereicht");
      await navigateTo("/berichtsheft");
      return;
    }
    if (target.dataset.action === "export-report-pdf") {
      event.preventDefault();
      await requireAuth();
      const response = await fetch("/api/training-reports/export.pdf", { headers: authHeaders() });
      if (!response.ok) {
        throw new Error("PDF-Export fehlgeschlagen");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "berichtsheft.pdf";
      link.click();
      URL.revokeObjectURL(url);
      showToast("PDF heruntergeladen");
      return;
    }
    if (target.dataset.action === "tz-iso") {
      event.preventDefault();
      const wrap = target.closest(".fk-tz-iso");
      wrap?.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn === target));
      updateToleranceCard(document.getElementById("screen-root") || document);
      return;
    }
    if (target.dataset.action === "tz-fit") {
      event.preventDefault();
      const root = document.getElementById("screen-root") || document;
      const hole = isoDeviations(root.querySelector(".fk-tz-iso button.active")?.dataset.iso || "H7");
      const shaft = isoDeviations("g6");
      const minClear = hole.ei - shaft.es;
      const result = root.querySelector(".fk-tz-result p");
      if (result) {
        result.innerHTML = `Spielpassung <span>— Mindestspiel:</span> <b>${minClear.toFixed(3)} mm</b>`;
      }
      showToast("Passung berechnet");
      return;
    }
    if (target.dataset.action === "sg-next" || target.dataset.action === "sg-prev" || target.dataset.action === "sg-phase") {
      event.preventDefault();
      const root = document.getElementById("screen-root") || document;
      let index = state.injectionPhase || 0;
      if (target.dataset.action === "sg-next") {
        index = Math.min(SG_PHASES.length - 1, index + 1);
      } else if (target.dataset.action === "sg-prev") {
        index = Math.max(0, index - 1);
      } else {
        index = Number(target.dataset.phase || 0);
      }
      renderInjectionPhase(root, index);
      return;
    }
    if (target.dataset.action === "ms-select") {
      event.preventDefault();
      state.caliperChoice = target.dataset.value;
      const wrap = target.closest(".fk-ms-options");
      wrap?.querySelectorAll(".fk-ms-opt").forEach((btn) => {
        const on = btn === target;
        btn.classList.toggle("selected", on);
        const img = btn.querySelector("img");
        if (img) {
          img.src = on ? "/static/figma/fk/fk-ms-radio-on.svg" : "/static/figma/fk/fk-ms-radio.svg";
        }
      });
      return;
    }
    if (target.dataset.action === "ms-submit") {
      event.preventDefault();
      const ok = String(state.caliperChoice || "23.5") === "23.5";
      showToast(ok ? "Richtig: 23 mm + 0.5 mm Nonius = 23.5 mm" : "Nicht ganz. Hauptskala 23 mm, Nonius 0.5 mm.");
      return;
    }
    if (target.dataset.action === "toast" && /Vorschlag übernommen|Vorschlag uebernommen/.test(target.dataset.toast || "")) {
      event.preventDefault();
      await requireAuth();
      const draft = await fetchJson("/api/training-reports/suggest", { headers: authHeaders() });
      const textarea = document.querySelector("textarea[name='activities'], textarea.bh-ne-input, textarea");
      if (textarea) {
        textarea.value = draft.activities;
      }
      showToast("Vorschlag aus Lernstand übernommen");
      return;
    }
    if (target.dataset.action === "toast" && /PDF/.test(target.dataset.toast || "")) {
      event.preventDefault();
      await requireAuth();
      const exported = await fetchJson("/api/training-reports/export", { headers: authHeaders() });
      const blob = new Blob([exported.body], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = exported.filename || "berichtsheft-export.txt";
      link.click();
      URL.revokeObjectURL(url);
      showToast("Berichtsheft-Export heruntergeladen");
      return;
    }
    if (target.dataset.action === "toast" && /Unterschrift/.test(target.dataset.toast || "")) {
      event.preventDefault();
      await requireAuth();
      const reports = state.trainingReports.length
        ? state.trainingReports
        : await fetchJson("/api/training-reports", { headers: authHeaders() });
      const draft = reports.find((row) => row.status === "draft") || reports[0];
      if (!draft) {
        showToast("Kein Eintrag zum Unterschreiben");
        return;
      }
      await fetchJson(`/api/training-reports/${draft.id}/sign`, {
        method: "POST",
        headers: authHeaders(),
      });
      await refreshPrivateData();
      showToast("Zur Unterschrift eingereicht");
      return;
    }
    if (target.dataset.action === "toast" && /Meldung gesendet/.test(target.dataset.toast || "")) {
      event.preventDefault();
      await requireAuth();
      const question = state.questions[state.currentQuestionIndex] || {};
      await fetchJson("/api/content/flags", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          entity_type: "quiz_question",
          entity_key: question.question_id || "unknown",
          reason: "meldung",
          notes: "Aus der App gemeldet.",
        }),
      });
      showToast("Meldung gespeichert");
      return;
    }
    if (target.dataset.action === "exam-submit-confirm") {
      event.preventDefault();
      await submitExamSession();
      return;
    }
    if (target.dataset.action === "practice-questions") {
      event.preventDefault();
      await startPracticeQuestions(target.dataset.practiceFilter || "all");
      return;
    }
    if (target.dataset.action === "practice-start") {
      event.preventDefault();
      state.practiceMode = "all";
      if (!state.allQuestions?.length) {
        await loadAllQuestions();
      }
      const pool = filteredPracticeQuestions();
      const full = practiceQuestionPool();
      if (!pool.length) {
        showToast("Keine Fragen in diesem Filter.");
        return;
      }
      state.questions = full;
      state.currentQuestionIndex = Math.max(
        0,
        full.findIndex((question) => question.question_id === pool[0].question_id),
      );
      await navigateTo("/lernen/frage");
      return;
    }
    if (target.dataset.action === "practice-filter") {
      event.preventDefault();
      state.practiceFilter = target.dataset.practiceFilter || "all";
      await navigateTo("/lernen/fragen");
      return;
    }
    if (target.dataset.action === "exam-kind-filter") {
      event.preventDefault();
      state.examKindFilter = target.dataset.examKind || "alle";
      bindExamHub(document.getElementById("screen-root") || document, { path: "/pruefungen" });
      return;
    }
    if (target.dataset.action === "exam-start-shortcut" || target.id === "exam-start") {
      event.preventDefault();
      const shortcut = target.closest("[data-action='exam-start-shortcut']") || target;
      const examId =
        shortcut.dataset.examId ||
        EXAM_SHORTCUT_IDS[shortcut.dataset.examKey || ""] ||
        null;
      await startExamShortcut(examId);
      return;
    }
    if (target.dataset.examAction === "choice" || target.closest("[data-exam-action='choice']")) {
      event.preventDefault();
      const button = target.closest("[data-exam-action='choice']") || target;
      await saveExamChoiceAnswer(button.dataset.questionId, Number(button.dataset.index));
      const progress = state.examProgress;
      if ((progress?.answered_count || 0) >= (progress?.total_questions || 0)) {
        await navigateTo("/pruefungen/abgabe", false);
      } else {
        await gotoNextExamQuestion();
      }
      return;
    }
    if (target.dataset.examAction === "next") {
      event.preventDefault();
      await gotoNextExamQuestion();
      return;
    }
    if (target.dataset.examAction === "prev") {
      event.preventDefault();
      await gotoPreviousExamQuestion();
      return;
    }
    if (target.dataset.examAction === "toggle-mark") {
      event.preventDefault();
      await toggleExamMark(getCurrentExamQuestion()?.question_id);
      return;
    }
    if (target.dataset.examAction === "goto-current") {
      event.preventDefault();
      await gotoExamQuestion(state.examProgress?.current_question_id);
      return;
    }
    if (target.dataset.examAction === "goto-question" || target.closest("[data-exam-action='goto-question']")) {
      event.preventDefault();
      const button = target.closest("[data-exam-action='goto-question']") || target;
      await gotoExamQuestion(button.dataset.questionId, Number(button.dataset.qIndex || "0"));
      return;
    }
    if (target.dataset.learnAction === "retry") {
      event.preventDefault();
      await advanceLearnQuestion(true);
      return;
    }
    if (target.dataset.learnAction === "next") {
      event.preventDefault();
      await advanceLearnQuestion(false);
      return;
    }
    if (target.dataset.action === "start-unit" || target.dataset.action === "start-next-unit") {
      event.preventDefault();
      await startLearnUnit(target.dataset.unitSlug || currentLearnUnit()?.slug);
      return;
    }
    if (target.dataset.action === "open-unit") {
      event.preventDefault();
      await openLearnUnit(target.dataset.unitSlug || currentLearnUnit()?.slug);
      return;
    }
    if (target.dataset.action === "next-formula") {
      event.preventDefault();
      const formulas = state.formulas || [];
      if (!formulas.length) {
        return;
      }
      const index = formulas.findIndex((item) => item.slug === state.activeFormulaSlug);
      const next = formulas[(index + 1 + formulas.length) % formulas.length];
      state.activeFormulaSlug = next.slug;
      renderFlashcard(document.getElementById("screen-root") || document, formulas);
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
      await navigateTo(resolvePostLoginRoute());
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
      await completeOnboardingFlow();
      return;
    }
    if (target.dataset.action === "save-language") {
      event.preventDefault();
      await saveLanguagePreference();
      return;
    }
    if (target.matches("[data-bind='level-up-continue']")) {
      event.preventDefault();
      const payload = loadLevelUp();
      const href = target.getAttribute("href") || payload?.returnTo || "/dashboard";
      clearLevelUp();
      if (href === LEARN_CONTINUE) {
        await goToNextLearnStep(false);
        return;
      }
      await navigateTo(href);
      return;
    }
    if (target.matches(".lang-row[data-lang]")) {
      event.preventDefault();
      state.selectedLanguage = target.dataset.lang || "de";
      const list = target.closest(".lang-list");
      if (list) {
        list.querySelectorAll(".lang-row[data-lang]").forEach((row) => {
          const selected = row === target;
          row.classList.toggle("active", selected);
          row.setAttribute("aria-selected", selected ? "true" : "false");
          const check = row.querySelector(".lang-check");
          const radio = row.querySelector(".lang-radio");
          if (check) {
            check.hidden = !selected;
          }
          if (radio) {
            radio.hidden = selected;
          }
        });
      }
      if (state.accessToken) {
        state.preferences = await fetchJson("/api/me/preferences", {
          method: "PUT",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify({ language: state.selectedLanguage }),
        });
        applyAppearance(state.preferences);
      }
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
      state.learnMonth = Number(target.dataset.month || "1");
      showToast(`Monat ${state.learnMonth}`);
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
    if (target.matches(".answer-option, .ld-answer") && target.dataset.index !== undefined) {
      const optionsRoot =
        target.closest("[data-bind='live-answers'], .ld-answers") || target.parentElement;
      optionsRoot.querySelectorAll(".answer-option, .ld-answer").forEach((el) => {
        el.classList.remove("selected");
      });
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
      const language = /english|englisch/i.test(label)
        ? "en"
        : /türk|tuerk|turk/i.test(label)
          ? "tr"
          : "de";
      if (state.accessToken) {
        await fetchJson("/api/me/preferences", {
          method: "PUT",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify({ language }),
        });
      }
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
      await navigateTo(resolvePostLoginRoute());
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
      await saveTrainingReport(form, "submitted");
    }
  } catch (error) {
    showToast(error.message);
    const feedback = form.parentElement?.querySelector("[data-feedback]");
    if (feedback) {
      feedback.textContent = error.message;
    }
  }
});

document.addEventListener("keydown", async (event) => {
  if (event.key !== "Enter") {
    return;
  }
  const input = event.target?.closest?.("[data-coach-input]");
  if (!input) {
    return;
  }
  event.preventDefault();
  const send = document.querySelector("[data-action='coach-send']");
  send?.click();
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

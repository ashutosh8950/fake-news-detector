/* ═══════════════════════════════════════════════════════════════════════════
   TruthScan — Premium Dashboard (vanilla JS, no dependencies)
   ═══════════════════════════════════════════════════════════════════════════ */
'use strict';

const API_BASE = '';           // same origin — FastAPI serves API + static files
const HEALTH_INTERVAL_MS = 30000;
const HISTORY_LIMIT = 10;

const STORAGE = {
  history: 'truthscan.history',
  stats:   'truthscan.stats',
  theme:   'truthscan.theme',
};

const SAMPLES = {
  fake: {
    title: 'BREAKING: Scientists Confirm 5G Towers Spread COVID-19',
    text: 'A leaked internal document from a top research institute has confirmed what many conspiracy theorists have been saying for months: 5G cellular towers are being used to spread the COVID-19 virus through electromagnetic frequencies. The document, obtained by whistleblowers inside the global health establishment, shows that government officials have been covering up the link between 5G rollout and pandemic spread. Thousands of protesters gathered outside telecom company headquarters demanding immediate shutdown of all 5G towers. Meanwhile, social media has exploded with videos showing birds dropping dead near newly activated towers. The mainstream media continues to suppress this information, but the truth is finally getting out.',
  },
  real: {
    title: 'Federal Reserve Holds Interest Rates Steady, Signals Patience on Cuts',
    text: 'The Federal Reserve left its benchmark interest rate unchanged on Wednesday, holding the federal funds rate in a range of 5.25% to 5.5% for the sixth consecutive meeting. In a statement following the two-day policy meeting, officials said inflation had eased over the past year but remained elevated, and that they did not expect it would be appropriate to reduce rates until they had gained greater confidence that inflation is moving sustainably toward the 2 percent objective. Chair Jerome Powell told reporters that recent data had not given policymakers greater confidence and that achieving that confidence would likely take longer than previously expected. Markets had largely anticipated the decision.',
  },
};

const ICONS = {
  fake: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>',
  real: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
};

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  history: loadJSON(STORAGE.history, []),
  stats:   loadJSON(STORAGE.stats, { total: 0, fake: 0, real: 0, confidenceSum: 0 }),
  theme:   localStorage.getItem(STORAGE.theme) || 'dark',
  busy:    false,
  modelInfo: null,
};

function loadJSON(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
  catch { return fallback; }
}
function saveJSON(key, value) { localStorage.setItem(key, JSON.stringify(value)); }

// ── DOM ──────────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const els = {
  statusDot:   $('status-dot'),
  statusText:  $('status-text'),
  statusPill:  $('status-pill'),
  themeToggle: $('theme-toggle'),
  menuToggle:  $('menu-toggle'),
  navLinks:    document.querySelector('.nav-links'),

  statTotal: $('stat-total'),
  statFake:  $('stat-fake'),
  statReal:  $('stat-real'),
  statAvg:   $('stat-avg'),

  form:       $('analyze-form'),
  headline:   $('headline'),
  article:    $('article'),
  charCount:  $('char-count'),
  clearForm:  $('clear-form'),
  sampleFake: $('sample-fake'),
  sampleReal: $('sample-real'),
  btnEnsemble: $('btn-ensemble'),
  btnDeep:     $('btn-deep'),
  errorBox:   $('error-box'),
  errorMsg:   $('error-msg'),

  loader:     $('loader'),
  loaderText: $('loader-text'),
  results:    $('results'),
  verdict:    $('verdict'),
  verdictIcon: $('verdict-icon'),
  verdictMode: $('verdict-mode'),
  verdictLabel: $('verdict-label'),
  verdictSub:  $('verdict-sub'),
  gauge:      $('gauge'),
  gaugeFill:  $('gauge-fill'),
  gaugeValue: $('gauge-value'),
  breakdown:  $('breakdown'),
  modelBars:  $('model-bars'),
  procTime:   $('proc-time'),

  donut:        $('donut'),
  donutValue:   $('donut-value'),
  donutCaption: $('donut-caption'),
  donutTotal:   $('donut-total'),
  legendFake:   $('legend-fake'),
  legendReal:   $('legend-real'),
  barChartBars: $('bar-chart-bars'),

  modelsGrid:   $('models-grid'),
  ensembleAccuracy: $('ensemble-accuracy'),
  historyList:  $('history-list'),
  clearHistory: $('clear-history'),
};

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(state.theme, false);
  initParticles();
  bindEvents();
  renderStats();
  renderCharts();
  renderHistory();
  checkHealth();
  loadModelInfo();
  setInterval(checkHealth, HEALTH_INTERVAL_MS);
  initScrollSpy();
});

// ── Events ───────────────────────────────────────────────────────────────────
function bindEvents() {
  els.form.addEventListener('submit', (e) => { e.preventDefault(); runAnalysis('ensemble'); });
  els.btnDeep.addEventListener('click', () => runAnalysis('deep'));

  els.article.addEventListener('input', updateCharCount);
  els.clearForm.addEventListener('click', () => {
    els.headline.value = '';
    els.article.value = '';
    updateCharCount();
    hideError();
    els.results.hidden = true;
  });
  els.sampleFake.addEventListener('click', () => loadSample('fake'));
  els.sampleReal.addEventListener('click', () => loadSample('real'));
  els.clearHistory.addEventListener('click', clearHistory);

  els.themeToggle.addEventListener('click', () => applyTheme(state.theme === 'dark' ? 'light' : 'dark', true));

  els.menuToggle.addEventListener('click', () => {
    const open = els.navLinks.classList.toggle('open');
    els.menuToggle.setAttribute('aria-expanded', String(open));
  });
  els.navLinks.addEventListener('click', (e) => {
    if (e.target.matches('.nav-link')) {
      els.navLinks.classList.remove('open');
      els.menuToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

function updateCharCount() {
  const n = els.article.value.length;
  els.charCount.textContent = `${n.toLocaleString()} character${n === 1 ? '' : 's'}`;
}

function loadSample(kind) {
  els.headline.value = SAMPLES[kind].title;
  els.article.value = SAMPLES[kind].text;
  updateCharCount();
  hideError();
  els.article.focus();
}

// ── Theme ────────────────────────────────────────────────────────────────────
function applyTheme(theme, persist) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  if (persist) localStorage.setItem(STORAGE.theme, theme);
}

// ── Scroll spy for nav links ─────────────────────────────────────────────────
function initScrollSpy() {
  const links = [...document.querySelectorAll('.nav-link[href^="#"]')];
  const sections = links.map((l) => document.querySelector(l.getAttribute('href'))).filter(Boolean);
  if (!('IntersectionObserver' in window) || !sections.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((l) => l.classList.toggle('active', l.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach((s) => observer.observe(s));
}

// ── Health ───────────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    if (data.status === 'ok' && data.models_loaded) {
      setStatus('online', 'API Online');
      if (!state.modelInfo) loadModelInfo();
    } else {
      setStatus('loading', 'Loading models…');
    }
  } catch {
    setStatus('offline', 'API Offline');
  }
}

function setStatus(kind, text) {
  els.statusDot.className = `status-dot ${kind}`;
  els.statusText.textContent = text;
  els.statusPill.title = text;
}

// ── Model info ───────────────────────────────────────────────────────────────
async function loadModelInfo() {
  try {
    const res = await fetch(`${API_BASE}/models/info`);
    if (!res.ok) throw new Error(res.statusText);
    state.modelInfo = await res.json();
    renderModelCards(state.modelInfo);
  } catch {
    if (!state.modelInfo) {
      els.modelsGrid.innerHTML = '<div class="models-error">Model metrics unavailable — the API may still be starting. Retrying with the next health check.</div>';
    }
  }
}

function renderModelCards(info) {
  const ensemble = info.ensemble;
  if (els.ensembleAccuracy) {
    els.ensembleAccuracy.textContent = ensemble && Number.isFinite(Number(ensemble.accuracy))
      ? `5-model ensemble accuracy: ${fmtPct2(ensemble.accuracy)}`
      : '5-model ensemble accuracy: unavailable';
  }

  const entries = Object.entries(info).filter(([key, m]) =>
    key !== 'ensemble' && m && typeof m === 'object' && 'accuracy' in m
  );
  if (!entries.length) {
    els.modelsGrid.innerHTML = '<div class="models-error">No model metrics reported.</div>';
    return;
  }
  entries.sort((a, b) => (b[1].accuracy ?? 0) - (a[1].accuracy ?? 0));

  els.modelsGrid.innerHTML = entries.map(([key, m], i) => {
    const brierScore = Number(m.brier_score);
    return `
      <article class="model-card glass reveal" style="--delay:${i * 0.08}s">
        <div class="model-card-head">
          <div>
            <div class="model-card-name">${escapeHtml(m.name || key)}</div>
            <div class="model-card-key">${escapeHtml(key)}</div>
          </div>
          <div class="model-acc">
            <strong data-count="${num(m.accuracy)}" data-suffix="%">0%</strong>
            <small>accuracy</small>
          </div>
        </div>
        <div class="metric-list">
          <div class="metric metric-single">
            <span>Brier score</span>
            <span class="metric-value">${Number.isFinite(brierScore) ? brierScore.toFixed(4) : 'n/a'}</span>
          </div>
        </div>
      </article>`;
  }).join('');

  requestAnimationFrame(() => {
    els.modelsGrid.querySelectorAll('.metric-fill').forEach((el) => { el.style.width = `${el.dataset.width}%`; });
    els.modelsGrid.querySelectorAll('[data-count]').forEach((el) => animateCount(el, Number(el.dataset.count), 1200, '%', 1));
  });
}

// ── Analysis ─────────────────────────────────────────────────────────────────
async function runAnalysis(mode) {
  if (state.busy) return;
  const text = els.article.value.trim();
  const title = els.headline.value.trim();

  if (text.length < 20) {
    showError('Please enter at least 20 characters of article text.');
    els.article.focus();
    return;
  }
  hideError();
  setBusy(true, mode);

  const endpoint = mode === 'deep' ? '/analyze/deep' : '/analyze';
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      if (res.status === 429 || err.error === 'rate_limited') {
        const retryAfter = Number(err.retry_after_seconds);
        const waitMessage = Number.isFinite(retryAfter) && retryAfter > 0
          ? ` Please wait ${retryAfter} seconds and try again.`
          : ' Please wait a moment and try again.';
        throw new Error(`You're sending requests too quickly.${waitMessage}`);
      }
      const detail = Array.isArray(err.detail) ? err.detail.map((d) => d.msg).join(', ') : err.detail;
      throw new Error(detail || `Server responded with ${res.status}`);
    }
    const data = await res.json();
    const result = normalizeResult(mode, data);
    renderResult(result);
    recordAnalysis(result, title || text);
  } catch (err) {
    showError(err.message || 'Could not reach the API. Is the server running?');
  } finally {
    setBusy(false, mode);
  }
}

/** Convert both /analyze and /analyze/deep payloads into one shape. */
function normalizeResult(mode, data) {
  if (mode === 'deep') {
    const label = String(data.label || '').toUpperCase();
    return {
      mode,
      isFake: label === 'FAKE',
      label: label || 'UNKNOWN',
      confidence: num(data.confidence),
      processingMs: data.processing_time_ms,
      models: [{ key: 'distilbert', name: 'DistilBERT (fine-tuned)', isFake: label === 'FAKE', label: data.label, confidence: num(data.confidence) }],
      subtitle: 'Transformer-based deep analysis',
    };
  }
  const models = Object.entries(data.models || {}).map(([key, m]) => ({
    key, name: m.name || key, isFake: !!m.is_fake, label: m.label, confidence: num(m.confidence),
  }));
  return {
    mode,
    isFake: !!data.ensemble_is_fake,
    label: String(data.ensemble_label || (data.ensemble_is_fake ? 'FAKE' : 'REAL')).toUpperCase(),
    confidence: num(data.overall_confidence),
    processingMs: data.processing_time_ms,
    models,
    subtitle: data.ensemble_is_fake
      ? `${data.fake_votes} of ${data.total_models} models flagged this as fake`
      : `${data.real_votes} of ${data.total_models} models classified this as real`,
  };
}

function renderResult(r) {
  const cls = r.isFake ? 'is-fake' : 'is-real';

  els.verdict.className = `verdict ${cls}`;
  els.verdictIcon.innerHTML = ICONS[r.isFake ? 'fake' : 'real'];
  els.verdictMode.textContent = r.mode === 'deep' ? 'DistilBERT verdict' : 'Ensemble verdict';
  els.verdictLabel.textContent = r.label;
  els.verdictSub.textContent = r.subtitle;

  // restart badge pop animation
  const badge = $('verdict-badge');
  badge.style.animation = 'none';
  void badge.offsetWidth;
  badge.style.animation = '';

  // gauge
  els.gauge.className = `gauge ${cls}`;
  const circumference = 2 * Math.PI * 52;
  els.gaugeFill.style.strokeDashoffset = circumference;
  requestAnimationFrame(() => {
    els.gaugeFill.style.strokeDashoffset = circumference * (1 - Math.min(r.confidence, 100) / 100);
  });
  animateCount(els.gaugeValue, r.confidence, 1400, '%', 1);

  // per-model breakdown
  const info = state.modelInfo || {};
  els.modelBars.innerHTML = r.models.map((m, i) => {
    const acc = info[m.key]?.accuracy;
    const mcls = m.isFake ? 'fake' : 'real';
    return `
      <div class="model-bar" style="--delay:${i * 0.08}s">
        <div class="model-bar-name">
          <strong>${escapeHtml(m.name)}</strong>
          <small>${acc != null ? `${fmtPct(acc)} accuracy` : 'accuracy n/a'}</small>
        </div>
        <div class="model-bar-track"><div class="model-bar-fill ${mcls}" data-width="${m.confidence}"></div></div>
        <div class="model-bar-value">
          <strong>${fmtPct(m.confidence)}</strong>
          <span class="tag ${mcls}">${escapeHtml(m.label || (m.isFake ? 'Fake' : 'Real'))}</span>
        </div>
      </div>`;
  }).join('');
  els.procTime.textContent = r.processingMs != null ? `processed in ${r.processingMs} ms` : '';

  els.results.hidden = false;
  requestAnimationFrame(() => {
    els.modelBars.querySelectorAll('.model-bar-fill').forEach((el) => { el.style.width = `${el.dataset.width}%`; });
  });
  els.results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function setBusy(busy, mode) {
  state.busy = busy;
  els.btnEnsemble.disabled = busy;
  els.btnDeep.disabled = busy;
  els.loader.hidden = !busy;
  if (busy) {
    els.results.hidden = true;
    els.loaderText.textContent = mode === 'deep' ? 'Running DistilBERT transformer…' : 'Running 5-model ensemble…';
    (mode === 'deep' ? els.btnDeep : els.btnEnsemble).classList.add('is-loading');
  } else {
    els.btnDeep.classList.remove('is-loading');
    els.btnEnsemble.classList.remove('is-loading');
  }
}

function showError(msg) {
  els.errorMsg.textContent = msg;
  els.errorBox.hidden = false;
}
function hideError() { els.errorBox.hidden = true; }

// ── Persistence: stats + history ─────────────────────────────────────────────
function recordAnalysis(r, snippetSource) {
  state.stats.total += 1;
  state.stats[r.isFake ? 'fake' : 'real'] += 1;
  state.stats.confidenceSum += r.confidence;
  saveJSON(STORAGE.stats, state.stats);

  state.history.unshift({
    id: Date.now(),
    ts: new Date().toISOString(),
    mode: r.mode,
    isFake: r.isFake,
    label: r.label,
    confidence: r.confidence,
    snippet: snippetSource.slice(0, 120),
  });
  state.history = state.history.slice(0, HISTORY_LIMIT);
  saveJSON(STORAGE.history, state.history);

  renderStats();
  renderCharts();
  renderHistory();
}

function clearHistory() {
  state.history = [];
  state.stats = { total: 0, fake: 0, real: 0, confidenceSum: 0 };
  saveJSON(STORAGE.history, state.history);
  saveJSON(STORAGE.stats, state.stats);
  renderStats();
  renderCharts();
  renderHistory();
}

function renderStats() {
  const { total, fake, real, confidenceSum } = state.stats;
  const avg = total ? confidenceSum / total : 0;
  animateCount(els.statTotal, total, 900);
  animateCount(els.statFake, fake, 900);
  animateCount(els.statReal, real, 900);
  animateCount(els.statAvg, avg, 900, '%', 1);
}

// ── Charts (pure CSS / vanilla JS) ───────────────────────────────────────────
function renderCharts() {
  // Donut — conic-gradient driven by --fake percentage
  const { total, fake, real } = state.stats;
  els.legendFake.textContent = fake;
  els.legendReal.textContent = real;
  els.donutTotal.textContent = `${total} ${total === 1 ? 'analysis' : 'analyses'}`;
  if (!total) {
    els.donut.classList.add('empty');
    els.donut.style.setProperty('--fake', 0);
    els.donutValue.textContent = '—';
    els.donutCaption.textContent = 'no data';
  } else {
    const fakePct = (fake / total) * 100;
    els.donut.classList.remove('empty');
    els.donut.style.setProperty('--fake', fakePct.toFixed(2));
    els.donutValue.textContent = `${Math.round(fakePct)}%`;
    els.donutCaption.textContent = 'flagged fake';
  }

  // Bar chart — last 10 confidence scores, oldest → newest
  const items = [...state.history].reverse();
  if (!items.length) {
    els.barChartBars.innerHTML = '<div class="bar-chart-empty">Run an analysis to see confidence history.</div>';
    return;
  }
  els.barChartBars.innerHTML = items.map((h, i) => `
    <div class="bar ${h.isFake ? 'fake' : 'real'}" data-value="${fmtPct(h.confidence)}" data-height="${h.confidence}"
         style="--delay:${i * 0.06}s" title="${escapeHtml(h.label)} — ${fmtPct(h.confidence)} • ${fmtTime(h.ts)}"></div>`).join('');
  requestAnimationFrame(() => {
    els.barChartBars.querySelectorAll('.bar').forEach((el) => { el.style.height = `${el.dataset.height}%`; });
  });
}

// ── History list ─────────────────────────────────────────────────────────────
function renderHistory() {
  if (!state.history.length) {
    els.historyList.innerHTML = '<li class="history-empty">No analyses yet — paste an article above to get started.</li>';
    return;
  }
  els.historyList.innerHTML = state.history.map((h, i) => `
    <li class="history-item" style="--delay:${i * 0.05}s">
      <span class="badge ${h.isFake ? 'fake' : 'real'}">${escapeHtml(h.label)}</span>
      <span class="history-snippet" title="${escapeHtml(h.snippet)}">
        ${escapeHtml(h.snippet)}
        <small>${h.mode === 'deep' ? 'DistilBERT' : 'Ensemble'}</small>
      </span>
      <span class="history-conf">${fmtPct(h.confidence)}</span>
      <time class="history-time" datetime="${h.ts}">${fmtTime(h.ts)}</time>
    </li>`).join('');
}

// ── Particles background ─────────────────────────────────────────────────────
function initParticles() {
  const canvas = $('particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W = 0, H = 0, particles = [];
  const COUNT = Math.min(90, Math.floor(window.innerWidth / 14));
  const COLORS = ['108,99,255', '0,212,255', '168,85,247'];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  function spawn() {
    return {
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 1.6 + 0.6, a: Math.random() * 0.45 + 0.15,
      c: COLORS[Math.floor(Math.random() * COLORS.length)],
    };
  }
  function frame() {
    ctx.clearRect(0, 0, W, H);
    const light = state.theme === 'light';
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx; p.y += p.vy;
      if (p.x < -10 || p.x > W + 10 || p.y < -10 || p.y > H + 10) particles[i] = spawn();
      for (let j = i + 1; j < particles.length; j++) {
        const q = particles[j];
        const dx = p.x - q.x, dy = p.y - q.y;
        const d = dx * dx + dy * dy;
        if (d < 130 * 130) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
          ctx.strokeStyle = `rgba(${p.c},${(light ? 0.12 : 0.08) * (1 - Math.sqrt(d) / 130)})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.c},${light ? p.a * 0.6 : p.a})`;
      ctx.fill();
    }
    if (!reduced) requestAnimationFrame(frame);
  }

  resize();
  window.addEventListener('resize', resize);
  particles = Array.from({ length: COUNT }, spawn);
  frame();
}

// ── Helpers ──────────────────────────────────────────────────────────────────
const activeCounters = new WeakMap();
function animateCount(el, to, duration, suffix = '', decimals = 0) {
  if (!el) return;
  const prev = activeCounters.get(el);
  if (prev) cancelAnimationFrame(prev);
  const from = parseFloat(el.textContent) || 0;
  const start = performance.now();
  const step = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    const val = from + (to - from) * ease;
    el.textContent = `${val.toFixed(decimals)}${suffix}`;
    if (t < 1) activeCounters.set(el, requestAnimationFrame(step));
    else activeCounters.delete(el);
  };
  activeCounters.set(el, requestAnimationFrame(step));
}

function num(v) { const n = Number(v); return Number.isFinite(n) ? Math.round(n * 100) / 100 : 0; }
function fmtPct(v) { return `${num(v).toFixed(1)}%`; }
function fmtPct2(v) {
  const n = Number(v);
  return Number.isFinite(n) ? `${n.toFixed(2)}%` : 'n/a';
}
function fmtTime(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`;
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

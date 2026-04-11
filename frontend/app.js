/* ═══════════════════════════════════════════════════════════════════════
   TruthScan — app.js
   Handles: API calls, results rendering, particles, history, theme, samples
   ═══════════════════════════════════════════════════════════════════════ */

'use strict';

// ── Config ──────────────────────────────────────────────────────────────────
const API_BASE = '';   // same origin — FastAPI serves both API + static files

// ── Sample articles ──────────────────────────────────────────────────────────
const SAMPLES = {
  fake: {
    title: 'BREAKING: Scientists Confirm 5G Towers Spread COVID-19',
    text: `A leaked internal document from a top research institute has confirmed what many conspiracy theorists have been saying for months: 5G cellular towers are being used to spread the COVID-19 virus through electromagnetic frequencies. The document, obtained by whistleblowers inside the global health establishment, shows that government officials have been covering up the link between 5G rollout and pandemic spread. Thousands of protesters gathered outside telecom company headquarters demanding immediate shutdown of all 5G towers. Meanwhile, social media has exploded with videos showing birds dropping dead near newly activated towers, and multiple doctors have come forward claiming they've seen patients whose symptoms directly correlate with 5G exposure. The mainstream media continues to suppress this information, but the truth is finally getting out.`
  },
  real: {
    title: 'Federal Reserve raises interest rates by 0.25% amid inflation concerns',
    text: `WASHINGTON (Reuters) - The Federal Reserve raised its benchmark overnight interest rate by a quarter of a percentage point on Wednesday and signaled it would continue increasing borrowing costs this year in its ongoing battle against inflation. The U.S. central bank's policy-setting Federal Open Market Committee raised its target federal funds rate to a range between 5.25% and 5.50%, the highest level in more than 22 years. Fed Chair Jerome Powell said at a press conference following the decision that he and his colleagues remain committed to returning inflation to the Fed's 2% target, though he noted that the central bank could pause or reverse course if economic conditions warrant. The move was widely expected by financial markets, which had priced in a roughly 98% chance of a quarter-point hike going into the meeting.`
  }
};

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  history: JSON.parse(localStorage.getItem('truthscan_history') || '[]'),
  isAnalyzing: false,
  theme: localStorage.getItem('truthscan_theme') || 'dark',
};

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const els = {
  form:         $('analyzer-form'),
  titleInput:   $('title-input'),
  newsInput:    $('news-input'),
  analyzeBtn:   $('analyze-btn'),
  btnText:      $('btn-text'),
  btnLoader:    $('btn-loader'),
  errorBox:     $('error-box'),
  errorMsg:     $('error-msg'),
  resultsCont:  $('results-container'),
  verdictCard:  $('verdict-card'),
  verdictIcon:  $('verdict-icon'),
  verdictIconW: $('verdict-icon-wrap'),
  verdictLabel: $('verdict-label'),
  verdictSub:   $('verdict-sub'),
  gaugeFill:    $('gauge-fill'),
  gaugePct:     $('gauge-pct'),
  gaugeBarAria: $('gauge-bar-aria'),
  fakeVotes:    $('fake-votes'),
  realVotes:    $('real-votes'),
  processTime:  $('processing-time'),
  modelsGrid:   $('models-grid'),
  historyList:  $('history-list'),
  statusDot:    $('status-dot'),
  statusText:   $('status-text'),
  textCount:    $('text-count'),
  themeToggle:  $('theme-toggle'),
  clearHistBtn: $('clear-history-btn'),
  sampleFake:   $('sample-fake-btn'),
  sampleReal:   $('sample-real-btn'),
  clearBtn:     $('clear-btn'),
};

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initParticles();
  checkHealth();
  renderHistory();
  bindEvents();
});

// ── Events ────────────────────────────────────────────────────────────────────
function bindEvents() {
  els.form.addEventListener('submit', handleSubmit);

  els.newsInput.addEventListener('input', () => {
    const words = els.newsInput.value.trim().split(/\s+/).filter(Boolean).length;
    els.textCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
  });

  els.sampleFake.addEventListener('click', () => loadSample('fake'));
  els.sampleReal.addEventListener('click', () => loadSample('real'));
  els.clearBtn.addEventListener('click', clearForm);
  els.clearHistBtn.addEventListener('click', clearHistory);
  els.themeToggle.addEventListener('click', toggleTheme);
}

// ── Sample loaders ────────────────────────────────────────────────────────────
function loadSample(type) {
  const s = SAMPLES[type];
  els.titleInput.value = s.title;
  els.newsInput.value  = s.text;
  // trigger word count update
  els.newsInput.dispatchEvent(new Event('input'));
  els.newsInput.focus();
}

function clearForm() {
  els.titleInput.value = '';
  els.newsInput.value  = '';
  els.textCount.textContent = '0 words';
  hideError();
}

// ── Form submit ───────────────────────────────────────────────────────────────
async function handleSubmit(e) {
  e.preventDefault();
  if (state.isAnalyzing) return;

  const text  = els.newsInput.value.trim();
  const title = els.titleInput.value.trim();

  if (text.length < 20) {
    showError('Please enter at least 20 characters of article text.');
    return;
  }

  hideError();
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const data = await res.json();
    renderResults(data, text, title);
    saveHistory({ text, title, data });

  } catch (err) {
    showError(err.message || 'Failed to connect to the server. Is it running?');
  } finally {
    setLoading(false);
  }
}

// ── Results rendering ─────────────────────────────────────────────────────────
function renderResults(data, text, title) {
  const isFake = data.ensemble_is_fake;
  const conf   = data.overall_confidence;

  // Verdict
  els.verdictCard.className  = `card verdict-card ${isFake ? 'is-fake' : 'is-real'}`;
  els.verdictIconW.className = `verdict-icon-wrap ${isFake ? 'is-fake' : 'is-real'}`;
  els.verdictIcon.textContent  = isFake ? '🚨' : '✅';
  els.verdictLabel.className   = `verdict-label ${isFake ? 'is-fake' : 'is-real'}`;
  els.verdictLabel.textContent = data.ensemble_label;
  els.verdictSub.textContent   =
    isFake
      ? `${data.fake_votes} of ${data.total_models} models identified this as fake.`
      : `${data.real_votes} of ${data.total_models} models classified this as real news.`;

  // Gauge — animate after short delay
  els.gaugeFill.className = `gauge-fill ${isFake ? 'is-fake' : 'is-real'}`;
  els.gaugeFill.style.width = '0%';
  els.gaugeBarAria.setAttribute('aria-valuenow', conf);
  requestAnimationFrame(() => {
    setTimeout(() => {
      els.gaugeFill.style.width = `${conf}%`;
    }, 100);
  });

  // Animate gauge percentage counter
  animateCounter(els.gaugePct, 0, conf, '%', 1200);

  // Vote tally
  els.fakeVotes.textContent = data.fake_votes;
  els.realVotes.textContent = data.real_votes;

  // Processing time
  if (data.processing_time_ms) {
    els.processTime.textContent = `⚡ Analyzed ${data.processed_length} tokens in ${data.processing_time_ms}ms`;
  }

  // Per-model breakdown
  els.modelsGrid.innerHTML = '';
  Object.entries(data.models).forEach(([key, m], idx) => {
    const isMFake = m.is_fake;
    const row = document.createElement('div');
    row.className = 'model-row';
    row.setAttribute('role', 'listitem');
    row.setAttribute('aria-label', `${m.name}: ${m.label} with ${m.confidence}% confidence`);
    row.innerHTML = `
      <div class="model-row-header">
        <span class="model-name">${m.name}</span>
        <span class="model-badge ${isMFake ? 'fake' : 'real'}">${m.label}</span>
      </div>
      <div class="model-conf-track">
        <div class="model-conf-fill ${isMFake ? 'fake' : 'real'}"
             id="mfill-${key}" style="width:0%"></div>
      </div>
      <div class="model-conf-label" id="mconf-${key}">0%</div>
    `;
    els.modelsGrid.appendChild(row);

    // Staggered animation
    setTimeout(() => {
      document.getElementById(`mfill-${key}`).style.width = `${m.confidence}%`;
      animateCounter(document.getElementById(`mconf-${key}`), 0, m.confidence, '%', 800);
    }, 200 + idx * 100);
  });

  // Show results
  els.resultsCont.hidden = false;
  els.resultsCont.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Counter animation ─────────────────────────────────────────────────────────
function animateCounter(el, from, to, suffix, duration) {
  const start = performance.now();
  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const value   = Math.round(from + (to - from) * ease);
    el.textContent = `${value}${suffix}`;
    if (progress < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// ── Health check ──────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const res  = await fetch(`${API_BASE}/health`);
    const data = await res.json();

    if (data.status === 'ok') {
      els.statusDot.className  = 'status-dot online';
      els.statusText.textContent = 'Models Ready';
    } else {
      setStatusLoading();
    }

    // Load model stats into hero bar
    loadModelStats();
  } catch {
    els.statusDot.className   = 'status-dot offline';
    els.statusText.textContent = 'Server Offline';
  }
}

async function loadModelStats() {
  try {
    const res  = await fetch(`${API_BASE}/models/info`);
    const meta = await res.json();

    const mapping = {
      lr:  'stat-lr', gbc: 'stat-gbc', rfc: 'stat-rfc',
      nb:  'stat-nb', dt:  'stat-dt',
    };

    Object.entries(mapping).forEach(([key, elId]) => {
      const el = $(elId);
      if (!el) return;
      el.classList.remove('loading-shimmer');
      const stat = meta[key];
      if (stat) {
        el.querySelector('.stat-val').textContent = `${stat.accuracy}%`;
      }
    });
  } catch {}
}

function setStatusLoading() {
  els.statusDot.className   = 'status-dot';
  els.statusText.textContent = 'Loading Models…';
}

// ── History ───────────────────────────────────────────────────────────────────
function saveHistory({ text, title, data }) {
  const item = {
    id:    Date.now(),
    label: data.ensemble_label,
    fake:  data.ensemble_is_fake,
    conf:  data.overall_confidence,
    snippet: (title || text).slice(0, 80),
  };
  state.history.unshift(item);
  if (state.history.length > 10) state.history.pop();
  localStorage.setItem('truthscan_history', JSON.stringify(state.history));
  renderHistory();
}

function renderHistory() {
  if (!state.history.length) {
    els.historyList.innerHTML = '<div class="history-empty">No analyses yet. Paste an article above to get started.</div>';
    return;
  }

  els.historyList.innerHTML = state.history.map(item => `
    <div class="history-item" role="listitem" tabindex="0" aria-label="${item.label}: ${item.snippet}">
      <span class="history-badge ${item.fake ? 'fake' : 'real'}">${item.label}</span>
      <span class="history-text">${escapeHtml(item.snippet)}…</span>
      <span class="history-pct">${item.conf}%</span>
    </div>
  `).join('');
}

function clearHistory() {
  state.history = [];
  localStorage.removeItem('truthscan_history');
  renderHistory();
}

// ── Theme ──────────────────────────────────────────────────────────────────────
function initTheme() {
  if (state.theme === 'light') document.body.classList.add('light-mode');
  els.themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.body.classList.toggle('light-mode');
  els.themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('truthscan_theme', state.theme);
}

// ── Loading state ─────────────────────────────────────────────────────────────
function setLoading(loading) {
  state.isAnalyzing = loading;
  els.analyzeBtn.disabled    = loading;
  els.btnText.style.opacity  = loading ? '0' : '1';
  if (loading) {
    els.btnLoader.classList.add('active');
    els.resultsCont.hidden = true;
  } else {
    els.btnLoader.classList.remove('active');
  }
}

function showError(msg) {
  els.errorMsg.textContent = msg;
  els.errorBox.hidden = false;
}

function hideError() {
  els.errorBox.hidden = true;
}

// ── Particle Canvas ───────────────────────────────────────────────────────────
function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function Particle() {
    this.reset();
  }

  Particle.prototype.reset = function() {
    this.x  = Math.random() * W;
    this.y  = Math.random() * H;
    this.vx = (Math.random() - 0.5) * 0.4;
    this.vy = (Math.random() - 0.5) * 0.4;
    this.r  = Math.random() * 1.5 + 0.5;
    this.a  = Math.random() * 0.4 + 0.1;
    this.color = Math.random() > 0.5 ? '99,179,237' : '159,122,234';
  };

  Particle.prototype.update = function() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > W || this.y < 0 || this.y > H) this.reset();
  };

  Particle.prototype.draw = function() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.color},${this.a})`;
    ctx.fill();
  };

  resize();
  window.addEventListener('resize', resize);

  // Create 80 particles
  for (let i = 0; i < 80; i++) particles.push(new Particle());

  function loop() {
    ctx.clearRect(0, 0, W, H);

    // Draw connection lines between nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(99,179,237,${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(loop);
  }

  loop();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function escapeHtml(str) {
  return str.replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c]));
}

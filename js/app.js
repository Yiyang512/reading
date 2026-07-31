// EmailJS (unchanged service)
(function () {
  if (window.emailjs) emailjs.init('_KKm93NyfWfCIx2nC');
})();

document.addEventListener('DOMContentLoaded', () => {
  const STORAGE = {
    user: 'hemiya_read_user',
    progress: 'hemiya_read_progress',
    settings: 'hemiya_read_settings'
  };
  const TIMERS = { A1: 8 * 60, A2: 10 * 60, B1: 12 * 60, B2: 15 * 60 };
  const EMAIL = { serviceID: 'service_fr7pas9', templateID: 'template_qk5xq0o' };

  const store = {
    get(k, fb = null) {
      try {
        const raw = localStorage.getItem(k);
        return raw ? JSON.parse(raw) : fb;
      } catch {
        return fb;
      }
    },
    set(k, v) {
      localStorage.setItem(k, JSON.stringify(v));
    }
  };

  const els = {
    contactSection: document.getElementById('contact-section'),
    contactForm: document.getElementById('contact-form'),
    formSuccess: document.getElementById('form-success'),
    formError: document.getElementById('form-error'),
    submitBtn: document.getElementById('submit-form'),
    app: document.getElementById('reading-app'),
    userChip: document.getElementById('user-chip'),
    resetUser: document.getElementById('reset-user'),
    levelButtons: [...document.querySelectorAll('.level-btn')],
    levelPanel: document.getElementById('level-panel'),
    levelTitle: document.getElementById('level-title'),
    levelExplanation: document.getElementById('level-explanation'),
    searchInput: document.getElementById('exercise-search'),
    exerciseGrid: document.getElementById('exercise-grid'),
    statsBar: document.getElementById('stats-bar'),
    sessionPanel: document.getElementById('session-panel'),
    backBtn: document.getElementById('back-btn'),
    exerciseTitle: document.getElementById('exercise-title'),
    exerciseMeta: document.getElementById('exercise-meta'),
    passageContent: document.getElementById('passage-content'),
    timerDisplay: document.getElementById('timer'),
    timerToggle: document.getElementById('timer-toggle'),
    timerReset: document.getElementById('timer-reset'),
    quizForm: document.getElementById('quiz-form'),
    results: document.getElementById('results'),
    scoreSummary: document.getElementById('score-summary'),
    scoreDetail: document.getElementById('score-detail'),
    retryBtn: document.getElementById('retry-btn'),
    nextBtn: document.getElementById('next-btn'),
    fontUp: document.getElementById('font-up'),
    fontDown: document.getElementById('font-down'),
    toast: document.getElementById('toast')
  };

  const state = {
    user: store.get(STORAGE.user),
    progress: store.get(STORAGE.progress, {}),
    settings: store.get(STORAGE.settings, { fontScale: 1 }),
    level: null,
    reading: null,
    filter: '',
    timerId: null,
    timeLeft: 0,
    timerRunning: false
  };

  function toast(msg, type = 'info') {
    els.toast.textContent = msg;
    els.toast.className = `toast show ${type}`;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => els.toast.classList.remove('show'), 3000);
  }

  function formatTime(sec) {
    const s = Math.max(0, Math.floor(sec || 0));
    return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  function notifyParentHeight() {
    const height = Math.ceil(document.documentElement.scrollHeight);
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'hemiya-read-resize', height }, '*');
    }
  }

  function key(level, id) {
    return `${level}:${id}`;
  }

  function showApp() {
    els.contactSection.classList.add('hidden');
    els.app.classList.remove('hidden');
    if (state.user) {
      els.userChip.textContent = `${state.user.fullName} · ${state.user.targetLevel}`;
      els.userChip.classList.remove('hidden');
      if (state.user.targetLevel) selectLevel(state.user.targetLevel);
    }
    applyFontScale();
    notifyParentHeight();
  }

  function validateField(id) {
    const field = document.getElementById(id);
    const err = document.getElementById(`${id}-error`);
    let ok = !!(field && String(field.value).trim());
    if (id === 'email' && ok) ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value.trim());
    field.classList.toggle('error', !ok);
    if (err) err.style.display = ok ? 'none' : 'block';
    return ok;
  }

  if (state.user) showApp();

  els.contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    els.formSuccess.classList.add('hidden');
    els.formError.classList.add('hidden');
    if (!(validateField('fullName') && validateField('email') && validateField('targetLevel'))) return;

    const payload = {
      fullName: document.getElementById('fullName').value.trim(),
      email: document.getElementById('email').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      targetLevel: document.getElementById('targetLevel').value
    };

    els.submitBtn.disabled = true;
    els.submitBtn.textContent = 'Submitting…';

    const templateParams = {
      name: payload.fullName,
      email: payload.email,
      reply_to: payload.email,
      time: new Date().toLocaleString(),
      message: `New reading-tool registration targeting ${payload.targetLevel}.\nEmail: ${payload.email}\nPhone: ${payload.phone || '—'}`
    };

    const unlock = () => {
      state.user = payload;
      store.set(STORAGE.user, payload);
      els.formSuccess.classList.remove('hidden');
      toast('Welcome! Opening your reading space…', 'success');
      setTimeout(showApp, 900);
    };

    if (!window.emailjs) {
      unlock();
      els.submitBtn.disabled = false;
      els.submitBtn.textContent = 'Start reading practice';
      return;
    }

    emailjs
      .send(EMAIL.serviceID, EMAIL.templateID, templateParams)
      .then(() => {
        unlock();
      })
      .catch((err) => {
        console.error(err);
        els.formError.classList.remove('hidden');
        // Soft-fail so learners are not blocked
        unlock();
      })
      .finally(() => {
        els.submitBtn.disabled = false;
        els.submitBtn.textContent = 'Start reading practice';
      });
  });

  els.resetUser.addEventListener('click', () => {
    localStorage.removeItem(STORAGE.user);
    location.reload();
  });

  function selectLevel(level) {
    state.level = level;
    els.levelButtons.forEach((b) => b.classList.toggle('active', b.dataset.level === level));
    els.levelTitle.textContent = `Niveau ${level}`;
    els.levelExplanation.textContent = levelDescriptions[level] || '';
    els.levelPanel.classList.remove('hidden');
    els.sessionPanel.classList.add('hidden');
    renderStats();
    renderGrid();
    notifyParentHeight();
  }

  els.levelButtons.forEach((btn) => btn.addEventListener('click', () => selectLevel(btn.dataset.level)));
  els.searchInput.addEventListener('input', () => {
    state.filter = els.searchInput.value.trim().toLowerCase();
    renderGrid();
  });

  function renderStats() {
    const list = readingData[state.level] || [];
    let done = 0;
    let sum = 0;
    let n = 0;
    list.forEach((ex) => {
      const p = state.progress[key(state.level, ex.id)];
      if (p) {
        done += 1;
        if (typeof p.percent === 'number') {
          sum += p.percent;
          n += 1;
        }
      }
    });
    els.statsBar.innerHTML = `
      <div class="stat"><span class="stat-value">${list.length}</span><span class="stat-label">Texts</span></div>
      <div class="stat"><span class="stat-value">${done}</span><span class="stat-label">Attempted</span></div>
      <div class="stat"><span class="stat-value">${n ? Math.round(sum / n) : 0}%</span><span class="stat-label">Avg score</span></div>
    `;
  }

  function wordCount(html) {
    const d = document.createElement('div');
    d.innerHTML = html || '';
    return (d.textContent || '').trim().split(/\s+/).filter(Boolean).length;
  }

  function renderGrid() {
    const list = (readingData[state.level] || []).filter((ex) => {
      if (!state.filter) return true;
      return ex.title.toLowerCase().includes(state.filter) || ex.id.toLowerCase().includes(state.filter);
    });
    els.exerciseGrid.innerHTML = '';
    if (!list.length) {
      els.exerciseGrid.innerHTML = `<p class="empty-state">No texts match your search.</p>`;
      return;
    }
    list.forEach((ex, idx) => {
      const p = state.progress[key(state.level, ex.id)];
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'exercise-card';
      card.innerHTML = `
        <div class="exercise-card-top">
          <span class="exercise-index">${String(idx + 1).padStart(2, '0')}</span>
          ${p ? `<span class="pill ${p.percent >= 70 ? 'good' : 'warn'}">${p.percent}%</span>` : '<span class="pill muted">New</span>'}
        </div>
        <h3>${ex.title}</h3>
        <p>${ex.questions.length} questions · ~${wordCount(ex.content)} words</p>
      `;
      card.addEventListener('click', () => openReading(ex.id));
      els.exerciseGrid.appendChild(card);
    });
    notifyParentHeight();
  }

  function openReading(id) {
    const list = readingData[state.level] || [];
    const reading = list.find((x) => x.id === id);
    if (!reading) return;
    state.reading = reading;
    els.levelPanel.classList.add('hidden');
    els.sessionPanel.classList.remove('hidden');
    els.results.classList.add('hidden');
    els.exerciseTitle.textContent = reading.title;
    els.exerciseMeta.textContent = `${state.level} · ${reading.questions.length} questions · ${wordCount(reading.content)} words`;
    els.passageContent.innerHTML = reading.content;
    buildQuiz(reading.questions);
    resetTimer();
    notifyParentHeight();
    window.scrollTo({ top: els.sessionPanel.offsetTop - 16, behavior: 'smooth' });
  }

  els.backBtn.addEventListener('click', () => {
    clearTimer(true);
    els.sessionPanel.classList.add('hidden');
    els.levelPanel.classList.remove('hidden');
    renderStats();
    renderGrid();
    notifyParentHeight();
  });

  function applyFontScale() {
    els.passageContent.style.fontSize = `${1.05 * (state.settings.fontScale || 1)}rem`;
  }
  els.fontUp.addEventListener('click', () => {
    state.settings.fontScale = Math.min(1.45, (state.settings.fontScale || 1) + 0.1);
    store.set(STORAGE.settings, state.settings);
    applyFontScale();
  });
  els.fontDown.addEventListener('click', () => {
    state.settings.fontScale = Math.max(0.9, (state.settings.fontScale || 1) - 0.1);
    store.set(STORAGE.settings, state.settings);
    applyFontScale();
  });

  function resetTimer() {
    clearTimer(false);
    state.timeLeft = TIMERS[state.level] || 600;
    els.timerDisplay.textContent = formatTime(state.timeLeft);
    els.timerDisplay.classList.remove('urgent');
    els.timerToggle.textContent = 'Start timer';
    els.timerToggle.disabled = false;
  }

  function clearTimer(resetLabel) {
    if (state.timerId) clearInterval(state.timerId);
    state.timerId = null;
    state.timerRunning = false;
    if (resetLabel) els.timerToggle.textContent = 'Start timer';
  }

  els.timerToggle.addEventListener('click', () => {
    if (state.timerRunning) {
      clearTimer(true);
      return;
    }
    state.timerRunning = true;
    els.timerToggle.textContent = 'Pause';
    state.timerId = setInterval(() => {
      state.timeLeft -= 1;
      els.timerDisplay.textContent = formatTime(state.timeLeft);
      if (state.timeLeft <= 30) els.timerDisplay.classList.add('urgent');
      if (state.timeLeft <= 0) {
        clearTimer(true);
        els.timerToggle.textContent = 'Time up';
        els.timerToggle.disabled = true;
        toast('Time is up — submitting your answers.', 'warn');
        gradeQuiz(true);
      }
    }, 1000);
  });
  els.timerReset.addEventListener('click', resetTimer);

  function buildQuiz(questions) {
    els.quizForm.innerHTML = '';
    questions.forEach((q, index) => {
      const block = document.createElement('div');
      block.className = 'question';
      block.id = q.id;
      block.innerHTML = `<p class="question-text"><span class="q-num">${index + 1}</span> ${q.question}</p>`;
      const options = document.createElement('div');
      options.className = 'options';

      if (q.type === 'radio' || q.type === 'checkbox') {
        q.options.forEach((opt) => {
          const row = document.createElement('label');
          row.className = 'option';
          row.innerHTML = `
            <input type="${q.type === 'radio' ? 'radio' : 'checkbox'}" name="${q.id}" value="${opt.id}" id="${q.id}-${opt.id}">
            <span>${opt.text}</span>
          `;
          options.appendChild(row);
        });
      } else {
        const ta = document.createElement('textarea');
        ta.id = `${q.id}-answer`;
        ta.name = q.id;
        ta.rows = 3;
        ta.placeholder = 'Votre réponse…';
        options.appendChild(ta);
      }

      const feedback = document.createElement('div');
      feedback.className = 'feedback';
      feedback.id = `feedback-${q.id}`;
      block.appendChild(options);
      block.appendChild(feedback);
      els.quizForm.appendChild(block);
    });

    const controls = document.createElement('div');
    controls.className = 'controls';
    controls.innerHTML = `
      <button type="submit" id="submit-quiz">Check answers</button>
      <button type="button" id="show-answers" class="ghost">Reveal answers</button>
    `;
    els.quizForm.appendChild(controls);
    document.getElementById('show-answers').addEventListener('click', revealAnswers);
  }

  els.quizForm.addEventListener('submit', (e) => {
    e.preventDefault();
    gradeQuiz(false);
  });

  function gradeQuiz() {
    if (!state.reading) return;
    clearTimer(true);
    const questions = state.reading.questions;
    let correct = 0;
    const details = [];

    questions.forEach((q) => {
      let isCorrect = false;
      if (q.type === 'radio') {
        const selected = document.querySelector(`input[name="${q.id}"]:checked`);
        isCorrect = !!(selected && selected.value === q.correctAnswer);
      } else if (q.type === 'checkbox') {
        const selected = [...document.querySelectorAll(`input[name="${q.id}"]:checked`)].map((i) => i.value);
        isCorrect = [...selected].sort().join(',') === [...q.correctAnswer].sort().join(',');
      } else {
        const val = (document.getElementById(`${q.id}-answer`).value || '').trim().toLowerCase();
        isCorrect = val.includes(String(q.correctAnswer).trim().toLowerCase());
      }
      if (isCorrect) correct += 1;
      showFeedback(q.id, isCorrect, q.explanation);
      markOptions(q);
      details.push({ isCorrect, explanation: q.explanation });
    });

    const percent = Math.round((correct / questions.length) * 100);
    els.scoreSummary.textContent = `${correct}/${questions.length} · ${percent}%`;
    els.scoreDetail.innerHTML = details
      .map(
        (d, i) =>
          `<div class="score-row ${d.isCorrect ? 'ok' : 'bad'}"><strong>Q${i + 1}</strong> ${d.isCorrect ? 'Correct' : 'Incorrect'}<span>${d.explanation}</span></div>`
      )
      .join('');
    els.results.classList.remove('hidden');

    state.progress[key(state.level, state.reading.id)] = {
      percent,
      correct,
      total: questions.length,
      at: Date.now()
    };
    store.set(STORAGE.progress, state.progress);
    renderStats();
    els.results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    notifyParentHeight();
    toast(percent >= 70 ? 'Nice work!' : 'Review the passage and try again.', percent >= 70 ? 'success' : 'info');
  }

  function showFeedback(id, isCorrect, explanation) {
    const box = document.getElementById(`feedback-${id}`);
    box.className = `feedback ${isCorrect ? 'correct' : 'incorrect'}`;
    box.innerHTML = `<p class="${isCorrect ? 'correct' : 'incorrect'}-feedback">${isCorrect ? 'Correct' : 'Incorrect'}</p><p>${explanation}</p>`;
  }

  function markOptions(q) {
    if (q.type !== 'radio' && q.type !== 'checkbox') return;
    q.options.forEach((opt) => {
      const input = document.getElementById(`${q.id}-${opt.id}`);
      const label = input && input.closest('label');
      if (!label) return;
      const isRight = q.type === 'radio' ? opt.id === q.correctAnswer : q.correctAnswer.includes(opt.id);
      label.classList.toggle('is-correct', isRight);
    });
  }

  function revealAnswers() {
    if (!state.reading) return;
    state.reading.questions.forEach((q) => {
      if (q.type === 'radio' || q.type === 'checkbox') {
        q.options.forEach((opt) => {
          const input = document.getElementById(`${q.id}-${opt.id}`);
          const label = input && input.closest('label');
          const isRight = q.type === 'radio' ? opt.id === q.correctAnswer : q.correctAnswer.includes(opt.id);
          if (isRight && label) label.classList.add('is-correct', 'highlight');
          if (isRight && input) input.checked = true;
        });
      } else {
        const ta = document.getElementById(`${q.id}-answer`);
        if (ta) {
          ta.value = q.correctAnswer;
          ta.classList.add('highlight');
        }
      }
      showFeedback(q.id, true, q.explanation);
    });
    notifyParentHeight();
  }

  els.retryBtn.addEventListener('click', () => state.reading && openReading(state.reading.id));
  els.nextBtn.addEventListener('click', () => {
    const list = readingData[state.level] || [];
    const idx = list.findIndex((x) => x.id === state.reading.id);
    openReading((list[idx + 1] || list[0]).id);
  });

  const ro = new ResizeObserver(() => notifyParentHeight());
  ro.observe(document.body);
  window.addEventListener('load', notifyParentHeight);
  applyFontScale();
});

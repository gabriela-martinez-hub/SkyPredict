// ── Generar estrellas decorativas ──
(function() {
  const container = document.getElementById('stars');
  for (let i = 0; i < 60; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    const size = Math.random() * 2.5 + 0.5;
    s.style.cssText = `
      width:${size}px; height:${size}px;
      top:${Math.random()*60}%;
      left:${Math.random()*100}%;
      animation-delay:${Math.random()*4}s;
      animation-duration:${2+Math.random()*3}s;
    `;
    container.appendChild(s);
  }
})();

let currentModel = null;

// ── Navegación ──
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function selectModel(model) {
  currentModel = model;
  showScreen('screen-' + model);
  loadSavedProgress(model);
}

function goBack() {
  currentModel = null;
  showScreen('screen-select');
}

// ── Guardar progreso en localStorage ──
function getFormData(model) {
  if (model === 'cancel') {
    return {
      year:        document.getElementById('c-year').value,
      month:       document.getElementById('c-month').value,
      day:         document.getElementById('c-day').value,
      dow:         document.getElementById('c-dow').value,
      carrier:     document.getElementById('c-carrier').value,
      depTime:     document.getElementById('c-dep-time').value,
      arrTime:     document.getElementById('c-arr-time').value,
      originState: document.getElementById('c-origin-state').value,
      destState:   document.getElementById('c-dest-state').value,
      originCity:  document.getElementById('c-origin-city').value,
      destCity:    document.getElementById('c-dest-city').value,
      distance:    document.getElementById('c-distance').value,
    };
  } else {
    return {
      year:        document.getElementById('d-year').value,
      month:       document.getElementById('d-month').value,
      day:         document.getElementById('d-day').value,
      dow:         document.getElementById('d-dow').value,
      carrier:     document.getElementById('d-carrier').value,
      depTime:     document.getElementById('d-dep-time').value,
      arrTime:     document.getElementById('d-arr-time').value,
      airtime:     document.getElementById('d-airtime').value,
      distance:    document.getElementById('d-distance').value,
      depDelay:    document.getElementById('d-dep-delay').value,
      originState: document.getElementById('d-origin-state').value,
      destState:   document.getElementById('d-dest-state').value,
      originCity:  document.getElementById('d-origin-city').value,
      destCity:    document.getElementById('d-dest-city').value,
    };
  }
}

function saveProgress(model) {
  const data = getFormData(model);
  localStorage.setItem('skypredict_' + model, JSON.stringify(data));

  const btn = document.getElementById('btn-save-' + model);
  const ind = document.getElementById('save-indicator-' + model);
  btn.classList.add('saved');
  btn.innerHTML = '<i class="bi bi-check-lg me-1"></i> ¡Guardado!';
  ind.textContent = new Date().toLocaleTimeString('es-CO', {hour:'2-digit', minute:'2-digit'});

  setTimeout(() => {
    btn.classList.remove('saved');
    btn.innerHTML = '<i class="bi bi-floppy me-1"></i> Guardar progreso';
  }, 2500);
}

function loadSavedProgress(model) {
  const raw = localStorage.getItem('skypredict_' + model);
  if (!raw) return;
  const d = JSON.parse(raw);

  if (model === 'cancel') {
    document.getElementById('c-year').value         = d.year        || '';
    document.getElementById('c-month').value        = d.month       || '';
    document.getElementById('c-day').value          = d.day         || '';
    document.getElementById('c-dow').value          = d.dow         || '';
    document.getElementById('c-carrier').value      = d.carrier     || '';
    document.getElementById('c-dep-time').value     = d.depTime     || '';
    document.getElementById('c-arr-time').value     = d.arrTime     || '';
    document.getElementById('c-origin-state').value = d.originState || '';
    document.getElementById('c-dest-state').value   = d.destState   || '';
    document.getElementById('c-origin-city').value  = d.originCity  || '';
    document.getElementById('c-dest-city').value    = d.destCity    || '';
    document.getElementById('c-distance').value     = d.distance    || '';
  } else {
    document.getElementById('d-year').value         = d.year        || '';
    document.getElementById('d-month').value        = d.month       || '';
    document.getElementById('d-day').value          = d.day         || '';
    document.getElementById('d-dow').value          = d.dow         || '';
    document.getElementById('d-carrier').value      = d.carrier     || '';
    document.getElementById('d-dep-time').value     = d.depTime     || '';
    document.getElementById('d-arr-time').value     = d.arrTime     || '';
    document.getElementById('d-airtime').value      = d.airtime     || '';
    document.getElementById('d-distance').value     = d.distance    || '';
    document.getElementById('d-dep-delay').value    = d.depDelay    || '';
    document.getElementById('d-origin-state').value = d.originState || '';
    document.getElementById('d-dest-state').value   = d.destState   || '';
    document.getElementById('d-origin-city').value  = d.originCity  || '';
    document.getElementById('d-dest-city').value    = d.destCity    || '';
  }

  const ind = document.getElementById('save-indicator-' + model);
  ind.textContent = '↩ Progreso restaurado';
}

// ── Enviar formulario y mostrar modal ──
function submitForm(model) {
  const data = getFormData(model);

  const empty = Object.values(data).some(v => v === '' || v === null);
  if (empty) {
    alert('Por favor completa todos los campos antes de predecir.');
    return;
  }

  const prob = Math.random();
  const isPositive = prob > 0.5;

  const badge   = document.getElementById('result-badge');
  const icon    = document.getElementById('result-icon');
  const label   = document.getElementById('result-label');
  const fill    = document.getElementById('result-prob-fill');
  const probTxt = document.getElementById('result-prob-text');
  const detail  = document.getElementById('result-detail');
  const title   = document.getElementById('modal-title');

  if (model === 'cancel') {
    title.textContent = 'Predicción · Cancelación de vuelo';
    if (isPositive) {
      badge.className    = 'result-badge positive';
      icon.className     = 'bi bi-x-circle-fill';
      label.textContent  = 'Vuelo CANCELADO';
      fill.className     = 'result-prob-fill high';
      detail.textContent = 'Alta probabilidad de que el vuelo sea cancelado.';
    } else {
      badge.className    = 'result-badge negative';
      icon.className     = 'bi bi-check-circle-fill';
      label.textContent  = 'No cancelado';
      fill.className     = 'result-prob-fill low';
      detail.textContent = 'Baja probabilidad de cancelación.';
    }
  } else {
    title.textContent = 'Predicción · Retraso ≥ 15 min';
    if (isPositive) {
      badge.className    = 'result-badge positive';
      icon.className     = 'bi bi-clock-history';
      label.textContent  = 'Retraso ≥ 15 min';
      fill.className     = 'result-prob-fill high';
      detail.textContent = 'Alta probabilidad de llegar con retraso significativo.';
    } else {
      badge.className    = 'result-badge negative';
      icon.className     = 'bi bi-check-circle-fill';
      label.textContent  = 'Llegada a tiempo';
      fill.className     = 'result-prob-fill low';
      detail.textContent = 'Baja probabilidad de retraso significativo.';
    }
  }

  const pct = Math.round(prob * 100);
  probTxt.textContent = pct + '%';
  setTimeout(() => { fill.style.width = pct + '%'; }, 100);

  const months  = ['','Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  const days    = ['','Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];
  const summary = document.getElementById('result-summary');
  summary.innerHTML = [
    chip('bi-calendar3',      `${data.day}/${months[+data.month]}/${data.year}`),
    chip('bi-calendar-week',  days[+data.dow] || data.dow),
    chip('bi-airplane',       data.carrier),
    chip('bi-geo-alt',        `${data.originCity || data.originState} → ${data.destCity || data.destState}`),
    chip('bi-clock',          `${data.depTime} → ${data.arrTime}`),
    data.distance ? chip('bi-rulers',          data.distance + ' mi') : '',
    data.airtime  ? chip('bi-hourglass-split', data.airtime + ' min aire') : '',
    data.depDelay !== undefined && data.depDelay !== ''
      ? chip('bi-stopwatch', '+' + data.depDelay + ' min salida') : '',
  ].join('');

  new bootstrap.Modal(document.getElementById('resultModal')).show();
}

function chip(icon, text) {
  return `<span class="summary-chip"><i class="bi ${icon}"></i>${text}</span>`;
}

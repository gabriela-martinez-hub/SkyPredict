// =============================================================
// SkyPredict — frontend.js v3
// Dropdowns con búsqueda + filtro ciudad por estado
// =============================================================

const BACKEND_URL = 'http://localhost:5000';

// ── Dataset exacto de estados → ciudades (extraído de flights_top3.csv) ──
const STATES_CITIES = {
  "AK": { name: "Alaska",          cities: ["Anchorage, AK","Fairbanks, AK","Juneau, AK"] },
  "AL": { name: "Alabama",         cities: ["Birmingham, AL","Huntsville, AL","Mobile, AL"] },
  "AR": { name: "Arkansas",        cities: ["Fayetteville, AR","Little Rock, AR"] },
  "AZ": { name: "Arizona",         cities: ["Phoenix, AZ","Tucson, AZ"] },
  "CA": { name: "California",      cities: ["Burbank, CA","Fresno, CA","Long Beach, CA","Los Angeles, CA","Oakland, CA","Ontario, CA","Palm Springs, CA","Sacramento, CA","San Diego, CA","San Francisco, CA","San Jose, CA","Santa Ana, CA","Santa Barbara, CA"] },
  "CO": { name: "Colorado",        cities: ["Colorado Springs, CO","Denver, CO","Eagle, CO","Gunnison, CO","Hayden, CO","Montrose/Delta, CO"] },
  "CT": { name: "Connecticut",     cities: ["Hartford, CT"] },
  "FL": { name: "Florida",         cities: ["Daytona Beach, FL","Fort Lauderdale, FL","Fort Myers, FL","Gainesville, FL","Jacksonville, FL","Key West, FL","Melbourne, FL","Miami, FL","Orlando, FL","Panama City, FL","Pensacola, FL","Sarasota/Bradenton, FL","Tallahassee, FL","Tampa, FL","Valparaiso, FL","West Palm Beach/Palm Beach, FL"] },
  "GA": { name: "Georgia",         cities: ["Atlanta, GA","Augusta, GA","Savannah, GA"] },
  "HI": { name: "Hawaii",          cities: ["Hilo, HI","Honolulu, HI","Kahului, HI","Kona, HI","Lihue, HI"] },
  "IA": { name: "Iowa",            cities: ["Cedar Rapids/Iowa City, IA","Des Moines, IA"] },
  "ID": { name: "Idaho",           cities: ["Boise, ID"] },
  "IL": { name: "Illinois",        cities: ["Bloomington/Normal, IL","Chicago, IL"] },
  "IN": { name: "Indiana",         cities: ["Evansville, IN","Indianapolis, IN","South Bend, IN"] },
  "KS": { name: "Kansas",          cities: ["Wichita, KS"] },
  "KY": { name: "Kentucky",        cities: ["Cincinnati, KY","Lexington, KY","Louisville, KY"] },
  "LA": { name: "Louisiana",       cities: ["Baton Rouge, LA","Lafayette, LA","New Orleans, LA","Shreveport, LA"] },
  "MA": { name: "Massachusetts",   cities: ["Boston, MA"] },
  "MD": { name: "Maryland",        cities: ["Baltimore, MD"] },
  "ME": { name: "Maine",           cities: ["Bangor, ME","Portland, ME"] },
  "MI": { name: "Michigan",        cities: ["Detroit, MI","Flint, MI","Grand Rapids, MI","Lansing, MI","Traverse City, MI"] },
  "MN": { name: "Minnesota",       cities: ["Duluth, MN","Minneapolis, MN"] },
  "MO": { name: "Missouri",        cities: ["Kansas City, MO","Springfield, MO","St. Louis, MO"] },
  "MS": { name: "Mississippi",     cities: ["Gulfport/Biloxi, MS","Jackson/Vicksburg, MS"] },
  "MT": { name: "Montana",         cities: ["Billings, MT","Bozeman, MT","Great Falls, MT","Kalispell, MT","Missoula, MT"] },
  "NC": { name: "North Carolina",  cities: ["Asheville, NC","Charlotte, NC","Fayetteville, NC","Greensboro/High Point, NC","Jacksonville/Camp Lejeune, NC","Raleigh/Durham, NC","Wilmington, NC"] },
  "ND": { name: "North Dakota",    cities: ["Bismarck/Mandan, ND","Fargo, ND","Minot, ND"] },
  "NE": { name: "Nebraska",        cities: ["Omaha, NE"] },
  "NH": { name: "New Hampshire",   cities: ["Manchester, NH"] },
  "NJ": { name: "New Jersey",      cities: ["Newark, NJ"] },
  "NM": { name: "New Mexico",      cities: ["Albuquerque, NM"] },
  "NV": { name: "Nevada",          cities: ["Las Vegas, NV","Reno, NV"] },
  "NY": { name: "New York",        cities: ["Albany, NY","Buffalo, NY","Islip, NY","New York, NY","Rochester, NY","Syracuse, NY","White Plains, NY"] },
  "OH": { name: "Ohio",            cities: ["Akron, OH","Cleveland, OH","Columbus, OH","Dayton, OH"] },
  "OK": { name: "Oklahoma",        cities: ["Oklahoma City, OK","Tulsa, OK"] },
  "OR": { name: "Oregon",          cities: ["Portland, OR"] },
  "PA": { name: "Pennsylvania",    cities: ["Allentown/Bethlehem/Easton, PA","Harrisburg, PA","Philadelphia, PA","Pittsburgh, PA","Scranton/Wilkes-Barre, PA"] },
  "PR": { name: "Puerto Rico",     cities: ["San Juan, PR"] },
  "RI": { name: "Rhode Island",    cities: ["Providence, RI"] },
  "SC": { name: "South Carolina",  cities: ["Charleston, SC","Columbia, SC","Greer, SC","Myrtle Beach, SC"] },
  "SD": { name: "South Dakota",    cities: ["Rapid City, SD","Sioux Falls, SD"] },
  "TN": { name: "Tennessee",       cities: ["Bristol/Johnson City/Kingsport, TN","Chattanooga, TN","Knoxville, TN","Memphis, TN","Nashville, TN"] },
  "TX": { name: "Texas",           cities: ["Amarillo, TX","Austin, TX","Corpus Christi, TX","Dallas, TX","Dallas/Fort Worth, TX","El Paso, TX","Harlingen/San Benito, TX","Houston, TX","Lubbock, TX","Midland/Odessa, TX","Mission/McAllen/Edinburg, TX","San Antonio, TX"] },
  "UT": { name: "Utah",            cities: ["Salt Lake City, UT"] },
  "VA": { name: "Virginia",        cities: ["Charlottesville, VA","Newport News/Williamsburg, VA","Norfolk, VA","Richmond, VA","Roanoke, VA","Washington, VA"] },
  "VI": { name: "Virgin Islands",  cities: ["Charlotte Amalie, VI","Christiansted, VI"] },
  "VT": { name: "Vermont",         cities: ["Burlington, VT"] },
  "WA": { name: "Washington",      cities: ["Pasco/Kennewick/Richland, WA","Seattle, WA","Spokane, WA"] },
  "WI": { name: "Wisconsin",       cities: ["Appleton, WI","Green Bay, WI","Madison, WI","Milwaukee, WI"] },
  "WV": { name: "West Virginia",   cities: ["Charleston/Dunbar, WV"] },
  "WY": { name: "Wyoming",         cities: ["Jackson, WY"] },
};

// ── Estado de los selects personalizados ──
// Cada select tiene: value (código), label (texto visible), dropdown abierto/cerrado
const selectState = {
  'origin-state': { value: '', label: '' },
  'dest-state':   { value: '', label: '' },
  'origin-city':  { value: '', label: '' },
  'dest-city':    { value: '', label: '' },
};

// ── Construir un custom-select a partir de un array de opciones ──
// options = [{ value, label, code? }]
function buildDropdown(wrapperId, options, placeholder) {
  const wrap = document.getElementById(wrapperId);
  if (!wrap) return;

  const key = wrapperId.replace('wrap-', '');
  const currentVal = selectState[key]?.value || '';

  // Renderizar trigger + dropdown
  wrap.innerHTML = `
    <div class="custom-select-trigger${options.length === 0 ? ' disabled' : ''}"
         id="trigger-${key}"
         tabindex="${options.length === 0 ? -1 : 0}"
         role="combobox" aria-expanded="false">
      <span id="label-${key}" class="${currentVal ? 'selected-val' : 'placeholder'}"
            style="${!currentVal ? 'color:var(--text-light);' : ''}">
        ${currentVal
          ? (selectState[key].label || currentVal)
          : placeholder}
      </span>
      <i class="bi bi-chevron-down cst-chevron"></i>
    </div>
    <div class="custom-select-dropdown" id="dropdown-${key}">
      <div class="csd-search-wrap">
        <i class="bi bi-search"></i>
        <input class="csd-search" id="search-${key}"
               type="text" placeholder="Buscar…" autocomplete="off" />
      </div>
      <div class="csd-options" id="options-${key}"></div>
    </div>
  `;

  renderOptions(key, options, '');

  // Events
  document.getElementById(`trigger-${key}`)
    .addEventListener('click', () => toggleDropdown(key));

  document.getElementById(`search-${key}`)
    .addEventListener('input', (e) => {
      renderOptions(key, options, e.target.value.toLowerCase());
    });

  // Cerrar con Escape
  wrap.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDropdown(key);
  });
}

function renderOptions(key, options, filter) {
  const container = document.getElementById(`options-${key}`);
  if (!container) return;

  const filtered = filter
    ? options.filter(o =>
        o.label.toLowerCase().includes(filter) ||
        (o.code && o.code.toLowerCase().includes(filter))
      )
    : options;

  if (filtered.length === 0) {
    container.innerHTML = `<div class="csd-empty">Sin resultados para "${filter}"</div>`;
    return;
  }

  container.innerHTML = filtered.map(o => `
    <div class="csd-option${selectState[key].value === o.value ? ' active' : ''}"
         data-value="${o.value}" data-label="${o.label}">
      ${o.code ? `<span class="opt-code">${o.code}</span>` : ''}
      ${o.label}
    </div>
  `).join('');

  container.querySelectorAll('.csd-option').forEach(el => {
    el.addEventListener('click', () => {
      selectOption(key, el.dataset.value, el.dataset.label);
    });
  });
}

function toggleDropdown(key) {
  const trigger  = document.getElementById(`trigger-${key}`);
  const dropdown = document.getElementById(`dropdown-${key}`);
  if (!trigger || trigger.classList.contains('disabled')) return;

  const isOpen = dropdown.classList.contains('open');

  // Cerrar todos
  closeAllDropdowns();

  if (!isOpen) {
    dropdown.classList.add('open');
    trigger.classList.add('open');
    trigger.setAttribute('aria-expanded', 'true');
    setTimeout(() => document.getElementById(`search-${key}`)?.focus(), 50);
  }
}

function closeDropdown(key) {
  document.getElementById(`dropdown-${key}`)?.classList.remove('open');
  document.getElementById(`trigger-${key}`)?.classList.remove('open');
  document.getElementById(`trigger-${key}`)?.setAttribute('aria-expanded', 'false');
}

function closeAllDropdowns() {
  Object.keys(selectState).forEach(closeDropdown);
}

function selectOption(key, value, label) {
  selectState[key] = { value, label };

  const labelEl  = document.getElementById(`label-${key}`);
  const searchEl = document.getElementById(`search-${key}`);

  if (labelEl) {
    labelEl.innerHTML  = label;
    labelEl.className  = 'selected-val';
    labelEl.removeAttribute('style');
  }
  if (searchEl) searchEl.value = '';

  closeDropdown(key);

  // Lógica de filtrado encadenado
  if (key === 'origin-state') {
    selectState['origin-city'] = { value: '', label: '' };
    const cities = buildCityOptions(value);
    buildDropdown('wrap-origin-city', cities, 'Selecciona ciudad');
    updateCityHint('origin-city-hint', value);
  }

  if (key === 'dest-state') {
    selectState['dest-city'] = { value: '', label: '' };
    const cities = buildCityOptions(value);
    buildDropdown('wrap-dest-city', cities, 'Selecciona ciudad');
    updateCityHint('dest-city-hint', value);
  }
}

function updateCityHint(hintId, stateCode) {
  const hint = document.getElementById(hintId);
  if (!hint) return;
  if (stateCode) {
    const stateName = STATES_CITIES[stateCode]?.name || stateCode;
    hint.innerHTML = `<i class="bi bi-info-circle"></i> Ciudades de ${stateName}`;
  } else {
    hint.innerHTML = `<i class="bi bi-info-circle"></i> Selecciona primero el estado`;
  }
}

// Construir opciones de estado
function buildStateOptions() {
  return Object.entries(STATES_CITIES)
    .sort((a, b) => a[1].name.localeCompare(b[1].name))
    .map(([code, data]) => ({
      value: code,
      label: data.name,
      code:  code,
    }));
}

// Construir opciones de ciudad dado un estado
function buildCityOptions(stateCode) {
  const data = STATES_CITIES[stateCode];
  if (!data) return [];
  return data.cities.map(city => ({ value: city, label: city }));
}

// ── Inicializar todos los selects ──
function initSelects() {
  const stateOptions = buildStateOptions();

  buildDropdown('wrap-origin-state', stateOptions, 'Selecciona estado');
  buildDropdown('wrap-dest-state',   stateOptions, 'Selecciona estado');
  buildDropdown('wrap-origin-city',  [],           'Selecciona ciudad');
  buildDropdown('wrap-dest-city',    [],           'Selecciona ciudad');
}

// Cerrar dropdowns al hacer clic fuera
document.addEventListener('click', (e) => {
  if (!e.target.closest('.custom-select-wrap')) {
    closeAllDropdowns();
  }
});

// ══════════════════════════════════════
// Navegación entre pantallas
// ══════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToForm() {
  const titulo = document.getElementById('form-title');
  titulo.innerHTML = `Formulario de Predicción`;
  showScreen('screen-form');
  loadSavedProgress();
}

function goBack() {
  showScreen('screen-select');
}

// ── Leer datos del formulario ──
function getFormData() {
  return {
    year:        document.getElementById('f-year').value,
    month:       document.getElementById('f-month').value,
    day:         document.getElementById('f-day').value,
    dow:         document.getElementById('f-dow').value,
    carrier:     document.getElementById('f-carrier').value,
    depTime:     document.getElementById('f-dep-time').value,
    arrTime:     document.getElementById('f-arr-time').value,
    originState: selectState['origin-state'].value,
    destState:   selectState['dest-state'].value,
    originCity:  selectState['origin-city'].value,
    destCity:    selectState['dest-city'].value,
  };
}

// ── Guardar y restaurar progreso ──
function saveProgress() {
  const data = getFormData();
  localStorage.setItem('skypredict_form', JSON.stringify(data));

  const btn = document.getElementById('btn-save-form');
  const ind = document.getElementById('save-indicator-form');
  btn.classList.add('saved');
  btn.innerHTML = '<i class="bi bi-check-lg me-1"></i> ¡Guardado!';
  ind.textContent = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });

  setTimeout(() => {
    btn.classList.remove('saved');
    btn.innerHTML = '<i class="bi bi-floppy me-1"></i> Guardar progreso';
  }, 2500);
}

function loadSavedProgress() {
  const raw = localStorage.getItem('skypredict_form');
  if (!raw) return;
  const d = JSON.parse(raw);

  if (d.year)    document.getElementById('f-year').value    = d.year;
  if (d.month)   document.getElementById('f-month').value   = d.month;
  if (d.day)     document.getElementById('f-day').value     = d.day;
  if (d.dow)     document.getElementById('f-dow').value     = d.dow;
  if (d.carrier) document.getElementById('f-carrier').value = d.carrier;
  if (d.depTime) document.getElementById('f-dep-time').value = d.depTime;
  if (d.arrTime) document.getElementById('f-arr-time').value = d.arrTime;

  // Restaurar selects personalizados
  if (d.originState) {
    const stateName = STATES_CITIES[d.originState]?.name || d.originState;
    selectOption('origin-state', d.originState, stateName);
    if (d.originCity) {
      setTimeout(() => selectOption('origin-city', d.originCity, d.originCity), 50);
    }
  }

  if (d.destState) {
    const stateName = STATES_CITIES[d.destState]?.name || d.destState;
    selectOption('dest-state', d.destState, stateName);
    if (d.destCity) {
      setTimeout(() => selectOption('dest-city', d.destCity, d.destCity), 50);
    }
  }
}

// ══════════════════════════════════════
// Enviar formulario al backend
// ══════════════════════════════════════
async function submitForm(modelo) {
  const data = getFormData();

  const empty = Object.values(data).some(v => v === '' || v === null || v === undefined);
  if (empty) {
    showFormError('Por favor completa todos los campos antes de predecir.');
    return;
  }

  const modal = new bootstrap.Modal(document.getElementById('resultModal'));
  document.getElementById('modal-title').textContent =
    modelo === 'cancel' ? 'Predicción · Cancelación de vuelo' : 'Predicción · Retraso ≥ 15 min';
  document.getElementById('modal-loading').style.display = 'block';
  document.getElementById('modal-result-content').style.display = 'none';
  modal.show();

  try {
    const response = await fetch(`${BACKEND_URL}/predict/${modelo}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });
    const resultado = await response.json();

    document.getElementById('modal-loading').style.display = 'none';
    document.getElementById('modal-result-content').style.display = 'block';
    mostrarResultado(resultado, data);

    setBackendStatus('ok');
  } catch (error) {
    document.getElementById('modal-loading').style.display = 'none';
    document.getElementById('modal-result-content').style.display = 'block';

    const prob = Math.random() * 0.4 + 0.1;
    const resultadoSimulado = {
      prediccion:   prob > 0.3 ? 1 : 0,
      probabilidad: parseFloat(prob.toFixed(4)),
      etiqueta: modelo === 'cancel'
        ? (prob > 0.3 ? 'Cancelado' : 'No cancelado')
        : (prob > 0.3 ? 'Retraso ≥ 15 min' : 'Llegada a tiempo'),
      modelo,
    };
    mostrarResultado(resultadoSimulado, data);
    setBackendStatus('error');
  }
}

function setBackendStatus(status) {
  const box  = document.getElementById('backend-status-box');
  const text = document.getElementById('backend-status-text');
  if (status === 'ok') {
    box.style.background  = '#f0fdf4';
    box.style.borderColor = '#bbf7d0';
    text.innerHTML = `<i class="bi bi-check-circle-fill me-1" style="color:#16a34a;"></i>
      <span style="color:#16a34a;font-weight:600;">Conexión exitosa</span>
      <span style="color:#64748b;"> — respuesta recibida de Flask en localhost:5000</span>`;
  } else {
    box.style.background  = '#fff7ed';
    box.style.borderColor = '#fed7aa';
    text.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1" style="color:#f97316;"></i>
      <span style="color:#f97316;font-weight:600;">Backend no disponible</span>
      <span style="color:#64748b;"> — resultado simulado. Ejecuta app.py para activar Flask.</span>`;
  }
}

// ── Renderizar resultado en el modal ──
function mostrarResultado(resultado, data) {
  const badge   = document.getElementById('result-badge');
  const icon    = document.getElementById('result-icon');
  const label   = document.getElementById('result-label');
  const fill    = document.getElementById('result-prob-fill');
  const probTxt = document.getElementById('result-prob-text');
  const detail  = document.getElementById('result-detail');

  const isPositive = resultado.prediccion === 1;
  const pct        = Math.round(resultado.probabilidad * 100);

  badge.className = isPositive ? 'result-badge positive' : 'result-badge negative';
  icon.className  = isPositive
    ? (resultado.modelo === 'cancel' ? 'bi bi-x-circle-fill' : 'bi bi-clock-history')
    : 'bi bi-check-circle-fill';
  fill.className = isPositive ? 'result-prob-fill high' : 'result-prob-fill low';

  detail.textContent = isPositive
    ? (resultado.modelo === 'cancel'
        ? 'Alta probabilidad de que el vuelo sea cancelado.'
        : 'Alta probabilidad de llegar con retraso significativo.')
    : (resultado.modelo === 'cancel'
        ? 'Baja probabilidad de cancelación.'
        : 'Baja probabilidad de retraso significativo.');

  label.textContent   = resultado.etiqueta;
  probTxt.textContent = pct + '%';
  setTimeout(() => { fill.style.width = pct + '%'; }, 100);

  // Resumen de datos
  const months  = ['','Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  const days    = ['','Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];
  const summary = document.getElementById('result-summary');
  summary.innerHTML = [
    chip('bi-calendar3',     `${data.day}/${months[+data.month]}/${data.year}`),
    chip('bi-calendar-week', days[+data.dow] || data.dow),
    chip('bi-airplane',      data.carrier),
    chip('bi-geo-alt',       `${data.originCity || data.originState} → ${data.destCity || data.destState}`),
    chip('bi-clock',         `${data.depTime} → ${data.arrTime}`),
  ].join('');
}

function chip(icon, text) {
  return `<span class="summary-chip"><i class="bi ${icon}"></i>${text}</span>`;
}

// ── Error de validación inline ──
function showFormError(msg) {
  let err = document.getElementById('form-error-msg');
  if (!err) {
    err = document.createElement('div');
    err.id = 'form-error-msg';
    err.style.cssText = `
      background:#fef2f2; border:1px solid #fca5a5; color:#dc2626;
      border-radius:8px; padding:0.6rem 1rem; font-size:0.84rem;
      margin-top:1rem; display:flex; align-items:center; gap:0.5rem;
    `;
    document.querySelector('#screen-form .d-flex').before(err);
  }
  err.innerHTML = `<i class="bi bi-exclamation-circle"></i> ${msg}`;
  err.style.display = 'flex';
  setTimeout(() => { err.style.display = 'none'; }, 4000);
}

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  initSelects();
});

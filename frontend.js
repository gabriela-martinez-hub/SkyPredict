// =============================================================
// frontend.js
// Proyecto: SkyPredict — Sistema Web de Predicción de Vuelos
// Descripción: Lógica del frontend. Maneja navegación, formulario,
//              comunicación con el backend Flask y visualización
//              del resultado en el modal.
// =============================================================

// URL base del backend Flask
const BACKEND_URL = 'http://localhost:5000';

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

// ── Estado actual ──
let currentModel = null;

// ── Navegación ──
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function selectModel(model) {
  currentModel = model;
  // Actualizar título del formulario según el modelo
  const titulo = document.getElementById('form-title');
  if (model === 'cancel') {
    titulo.innerHTML = `<i class="bi bi-x-circle-fill me-2" style="color:var(--sunset-1);font-size:1.4rem;"></i>Predicción de Cancelación`;
  } else {
    titulo.innerHTML = `<i class="bi bi-clock-history me-2" style="color:var(--sky-light);font-size:1.4rem;"></i>Predicción de Retraso ≥ 15 min`;
  }
  showScreen('screen-form');
  loadSavedProgress();
}

function goBack() {
  currentModel = null;
  showScreen('screen-select');
}

function goToForm() {
  // Lleva al formulario sin preseleccionar modelo —
  // el usuario decide con los dos botones de predicción
  document.getElementById('form-title').innerHTML =
    `<i class="bi bi-ui-checks me-2" style="color:var(--sunset-1);font-size:1.4rem;"></i>Formulario de Predicción`;
  showScreen('screen-form');
  loadSavedProgress();
}

// ── Leer datos del formulario unificado ──
function getFormData() {
  return {
    year:        document.getElementById('f-year').value,
    month:       document.getElementById('f-month').value,
    day:         document.getElementById('f-day').value,
    dow:         document.getElementById('f-dow').value,
    carrier:     document.getElementById('f-carrier').value,
    depTime:     document.getElementById('f-dep-time').value,
    arrTime:     document.getElementById('f-arr-time').value,
    originState: document.getElementById('f-origin-state').value,
    destState:   document.getElementById('f-dest-state').value,
    originCity:  document.getElementById('f-origin-city').value,
    destCity:    document.getElementById('f-dest-city').value,
  };
}

// ── Guardar y restaurar progreso (localStorage) ──
function saveProgress() {
  const data = getFormData();
  localStorage.setItem('skypredict_form', JSON.stringify(data));

  const btn = document.getElementById('btn-save-form');
  const ind = document.getElementById('save-indicator-form');
  btn.classList.add('saved');
  btn.innerHTML = '<i class="bi bi-check-lg me-1"></i> ¡Guardado!';
  ind.textContent = new Date().toLocaleTimeString('es-CO', {hour:'2-digit', minute:'2-digit'});

  setTimeout(() => {
    btn.classList.remove('saved');
    btn.innerHTML = '<i class="bi bi-floppy me-1"></i> Guardar progreso';
  }, 2500);
}

function loadSavedProgress() {
  const raw = localStorage.getItem('skypredict_form');
  if (!raw) return;
  const d = JSON.parse(raw);

  document.getElementById('f-year').value         = d.year        || '';
  document.getElementById('f-month').value        = d.month       || '';
  document.getElementById('f-day').value          = d.day         || '';
  document.getElementById('f-dow').value          = d.dow         || '';
  document.getElementById('f-carrier').value      = d.carrier     || '';
  document.getElementById('f-dep-time').value     = d.depTime     || '';
  document.getElementById('f-arr-time').value     = d.arrTime     || '';
  document.getElementById('f-origin-state').value = d.originState || '';
  document.getElementById('f-dest-state').value   = d.destState   || '';
  document.getElementById('f-origin-city').value  = d.originCity  || '';
  document.getElementById('f-dest-city').value    = d.destCity    || '';

  document.getElementById('save-indicator-form').textContent = '↩ Progreso restaurado';
}

// ── Enviar formulario al backend ──
async function submitForm(modelo) {
  const data = getFormData();

  // Validación: campos vacíos
  const empty = Object.values(data).some(v => v === '' || v === null);
  if (empty) {
    alert('Por favor completa todos los campos antes de predecir.');
    return;
  }

  // Abrir modal y mostrar spinner
  const modal = new bootstrap.Modal(document.getElementById('resultModal'));
  document.getElementById('modal-title').textContent =
    modelo === 'cancel' ? 'Predicción · Cancelación de vuelo' : 'Predicción · Retraso ≥ 15 min';
  document.getElementById('modal-loading').style.display = 'block';
  document.getElementById('modal-result-content').style.display = 'none';
  modal.show();

  try {
    // ── Llamada real al backend Flask ──
    const response = await fetch(`${BACKEND_URL}/predict/${modelo}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data)
    });

    const resultado = await response.json();

    // Ocultar spinner y mostrar resultado
    document.getElementById('modal-loading').style.display = 'none';
    document.getElementById('modal-result-content').style.display = 'block';

    // Mostrar resultado en el modal
    mostrarResultado(resultado, data);

    // ✅ Notificación de conexión exitosa con el backend
    const statusBox  = document.getElementById('backend-status-box');
    const statusText = document.getElementById('backend-status-text');
    statusBox.style.background = 'rgba(100,200,120,0.12)';
    statusBox.style.border     = '1px solid rgba(100,200,120,0.3)';
    statusText.innerHTML = `<i class="bi bi-check-circle-fill me-1" style="color:#7ddb95;"></i>
      <span style="color:#7ddb95;">Conexión con el backend exitosa</span>
      <span class="text-white-50"> — respuesta recibida de Flask en localhost:5000</span>`;

  } catch (error) {
    // ❌ Backend no disponible — mostrar resultado simulado con aviso
    document.getElementById('modal-loading').style.display = 'none';
    document.getElementById('modal-result-content').style.display = 'block';

    // Resultado simulado de respaldo
    const prob = Math.random() * 0.4 + 0.1;
    const resultadoSimulado = {
      prediccion:   prob > 0.3 ? 1 : 0,
      probabilidad: parseFloat(prob.toFixed(4)),
      etiqueta:     modelo === 'cancel'
        ? (prob > 0.3 ? 'Cancelado' : 'No cancelado')
        : (prob > 0.3 ? 'Retraso ≥ 15 min' : 'Llegada a tiempo'),
      modelo
    };
    mostrarResultado(resultadoSimulado, data);

    // ⚠️ Aviso de que el backend no estaba activo
    const statusBox  = document.getElementById('backend-status-box');
    const statusText = document.getElementById('backend-status-text');
    statusBox.style.background = 'rgba(244,162,97,0.1)';
    statusBox.style.border     = '1px solid rgba(244,162,97,0.3)';
    statusText.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1" style="color:var(--sunset-1);"></i>
      <span style="color:var(--sunset-1);">Backend no disponible</span>
      <span class="text-white-50"> — resultado simulado. Ejecuta app.py para activar Flask.</span>`;
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

  if (isPositive) {
    badge.className    = 'result-badge positive';
    icon.className     = resultado.modelo === 'cancel' ? 'bi bi-x-circle-fill' : 'bi bi-clock-history';
    fill.className     = 'result-prob-fill high';
    detail.textContent = resultado.modelo === 'cancel'
      ? 'Alta probabilidad de que el vuelo sea cancelado.'
      : 'Alta probabilidad de llegar con retraso significativo.';
  } else {
    badge.className    = 'result-badge negative';
    icon.className     = 'bi bi-check-circle-fill';
    fill.className     = 'result-prob-fill low';
    detail.textContent = resultado.modelo === 'cancel'
      ? 'Baja probabilidad de cancelación.'
      : 'Baja probabilidad de retraso significativo.';
  }

  label.textContent   = resultado.etiqueta;
  probTxt.textContent = pct + '%';
  setTimeout(() => { fill.style.width = pct + '%'; }, 100);

  // Resumen de datos ingresados
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

# =============================================================
# Proyecto: SkyPredict — Sistema Web de Predicción de Vuelos
# Descripción: Backend con Flask que expone la API de predicción.
#              Recibe datos del formulario desde el frontend,
#              los preprocesa y devuelve una predicción.
#
# Endpoints:
#   GET  /              → Sirve el frontend (index.html)
#   POST /predict/cancel → Predicción de cancelación de vuelo
#   POST /predict/delay  → Predicción de retraso >= 15 min
# =============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Permite que el frontend se conecte al backend

# -------------------------------------------------------------
# Tablas de codificación (Label Encoding)
# -------------------------------------------------------------
# Estas tablas replican la codificación aplicada en preprocessing.py.
# Cuando el frontend envía "WN", el backend lo convierte al entero
# correspondiente antes de pasarlo al modelo.
#
# En la Entrega 3 estos mapeos serán reemplazados por los encoders
# guardados (joblib) durante el entrenamiento real del modelo.

CARRIER_MAP = {'AA': 0, 'DL': 1, 'WN': 2}

# Nota: Los mapeos de estados y ciudades se generarán en Entrega 3
# a partir del LabelEncoder ajustado sobre flights_processed.csv.
# Por ahora se usa un hash numérico como aproximación.

def codificar_texto(valor):
    """
    Codificación temporal para variables de texto (estados y ciudades).
    Convierte el string a un entero usando hash, normalizado a un rango
    positivo. En Entrega 3 será reemplazado por LabelEncoder real.
    """
    return abs(hash(str(valor).strip().upper())) % 10000

def hhmm_a_minutos(valor_str):
    """
    Convierte hora en formato 'HH:MM' (del input type=time del HTML)
    a minutos totales desde medianoche.
    Ejemplo: '14:30' → 14*60 + 30 = 870.0
    """
    try:
        partes = str(valor_str).split(':')
        horas   = int(partes[0])
        minutos = int(partes[1]) if len(partes) > 1 else 0
        return float(horas * 60 + minutos)
    except Exception:
        return 0.0

def preprocesar_entrada(datos, modelo):
    """
    Transforma el JSON recibido del frontend al vector de features
    que espera el modelo de ML.

    Parámetros:
        datos  (dict): JSON enviado por el formulario del frontend.
        modelo (str):  'cancel' o 'delay'.

    Retorna:
        pd.DataFrame con una sola fila lista para predecir.

    Orden de columnas (debe coincidir con el entrenamiento):
        YEAR, MONTH, DAY_OF_MONTH, DAY_OF_WEEK,
        OP_UNIQUE_CARRIER, CRS_DEP_TIME, CRS_ARR_TIME,
        DEP_DELAY_NEW (solo para delay),
        ORIGIN_STATE_ABR, DEST_STATE_ABR,
        ORIGIN_CITY_NAME, DEST_CITY_NAME
    """
    features = {
        'YEAR':              int(datos.get('year', 2019)),
        'MONTH':             int(datos.get('month', 1)),
        'DAY_OF_MONTH':      int(datos.get('day', 1)),
        'DAY_OF_WEEK':       int(datos.get('dow', 1)),
        'OP_UNIQUE_CARRIER': CARRIER_MAP.get(datos.get('carrier', 'WN'), 2),
        'CRS_DEP_TIME':      hhmm_a_minutos(datos.get('depTime', '08:00')),
        'CRS_ARR_TIME':      hhmm_a_minutos(datos.get('arrTime', '10:00')),
        'ORIGIN_STATE_ABR':  codificar_texto(datos.get('originState', '')),
        'DEST_STATE_ABR':    codificar_texto(datos.get('destState', '')),
        'ORIGIN_CITY_NAME':  codificar_texto(datos.get('originCity', '')),
        'DEST_CITY_NAME':    codificar_texto(datos.get('destCity', '')),
    }

    # Nota: DEP_DELAY_NEW fue eliminada. El modelo predice ANTES del vuelo,
    # por lo tanto el usuario no conoce aún el retraso en salida.

    return pd.DataFrame([features])

# -------------------------------------------------------------
# GET / — Sirve el frontend
# -------------------------------------------------------------
@app.route('/')
def index():
    """
    Sirve el archivo index.html al abrir el navegador.
    Flask busca el archivo en la misma carpeta que app.py.
    """
    return send_from_directory('.', 'index.html')

# -------------------------------------------------------------
# POST /predict/cancel — Predicción de cancelación de vuelo
# -------------------------------------------------------------
@app.route('/predict/cancel', methods=['POST'])
def predict_cancel():
    """
    Recibe los datos del formulario de cancelación y devuelve
    la predicción del modelo.

    Entrada (JSON del frontend):
    {
        "year":        "2019",
        "month":       "3",
        "day":         "15",
        "dow":         "5",
        "carrier":     "WN",
        "depTime":     "08:30",
        "arrTime":     "10:45",
        "originState": "TX",
        "destState":   "CA",
        "originCity":  "Dallas",
        "destCity":    "Los Angeles"
    }

    Salida (JSON al frontend):
    {
        "prediccion":   0,          (0 = no cancelado, 1 = cancelado)
        "probabilidad": 0.03,       (probabilidad de cancelación)
        "etiqueta":     "No cancelado",
        "modelo":       "cancel"
    }
    """
    try:
        datos = request.get_json()

        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400

        # Preprocesar entrada
        X = preprocesar_entrada(datos, 'cancel')

        # ── PLACEHOLDER ──────────────────────────────────────────
        # En Entrega 3 esta línea se reemplaza por:
        #   prob = modelo_cancel.predict_proba(X)[0][1]
        #   pred = int(modelo_cancel.predict(X)[0])
        # Por ahora simulamos una probabilidad baja de cancelación
        # basada en el mes (invierno = más cancelaciones).
        mes = int(datos.get('month', 6))
        prob = 0.08 if mes in [12, 1, 2] else 0.03
        pred = 1 if prob > 0.5 else 0
        # ─────────────────────────────────────────────────────────

        return jsonify({
            'prediccion':   pred,
            'probabilidad': round(prob, 4),
            'etiqueta':     'Cancelado' if pred == 1 else 'No cancelado',
            'modelo':       'cancel'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# POST /predict/delay — Predicción de retraso >= 15 min
# -------------------------------------------------------------
@app.route('/predict/delay', methods=['POST'])
def predict_delay():
    """
    Recibe los datos del formulario de retraso y devuelve
    la predicción del modelo.

    Entrada (JSON del frontend):
    {
        "year":        "2019",
        "month":       "6",
        "day":         "20",
        "dow":         "4",
        "carrier":     "DL",
        "depTime":     "07:00",
        "arrTime":     "09:30",
        "originState": "GA",
        "destState":   "NY",
        "originCity":  "Atlanta",
        "destCity":    "New York"
    }

    Salida (JSON al frontend):
    {
        "prediccion":   1,          (0 = a tiempo, 1 = retraso >= 15 min)
        "probabilidad": 0.72,       (probabilidad de retraso significativo)
        "etiqueta":     "Retraso >= 15 min",
        "modelo":       "delay"
    }
    """
    try:
        datos = request.get_json()

        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400

        # Preprocesar entrada
        X = preprocesar_entrada(datos, 'delay')

        # ── PLACEHOLDER ──────────────────────────────────────────
        # En Entrega 3 esta línea se reemplaza por:
        #   prob = modelo_delay.predict_proba(X)[0][1]
        #   pred = int(modelo_delay.predict(X)[0])
        # Por ahora simulamos probabilidad basada en el mes y aerolínea.
        mes      = int(datos.get('month', 6))
        carrier  = datos.get('carrier', 'WN')
        prob = 0.35 if mes in [12, 1, 2, 6, 7] else 0.22
        prob = min(0.95, prob + (0.05 if carrier == 'WN' else 0))
        pred = 1 if prob >= 0.5 else 0
        # ─────────────────────────────────────────────────────────

        return jsonify({
            'prediccion':   pred,
            'probabilidad': round(prob, 4),
            'etiqueta':     'Retraso ≥ 15 min' if pred == 1 else 'Llegada a tiempo',
            'modelo':       'delay'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# Punto de entrada
# -------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 50)
    print("  SkyPredict — Backend Flask")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)

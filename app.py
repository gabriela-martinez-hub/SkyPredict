# =============================================================
# Proyecto: SkyPredict — Backend Flask
# Descripción: API de predicción de vuelos.
#              Carga los modelos KNN entrenados (.pkl) al iniciar
#              y los usa para predecir en cada request.
#
# Endpoints:
#   GET  /                     → Sirve el frontend (index.html)
#   GET  /<filename>           → Sirve archivos estáticos (CSS, JS)
#   GET  /api/ciudades/<state> → Devuelve ciudades de un estado
#   GET  /api/status           → Estado del backend y modelos cargados
#   POST /predict/cancel       → Predicción de cancelación de vuelo
#   POST /predict/delay        → Predicción de retraso >= 15 min
# =============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib
import os

# -------------------------------------------------------------
# Inicialización
# -------------------------------------------------------------
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

RUTA_MODELOS = 'models'

# -------------------------------------------------------------
# Carga de modelos al arrancar el servidor
# -------------------------------------------------------------
# Los modelos se cargan UNA SOLA VEZ cuando Flask inicia.
# Si un archivo .pkl no existe (aún no se corrió train_knn.py o train_red_neuronal.py), 
# el servidor igual arranca pero devuelve un error claro al predecir.
#
# Archivos esperados en la carpeta models/ para el KNN:
#   modelo_knn_cancel.pkl  → KNN entrenado para CANCELLED
#   scaler_knn_cancel.pkl  → StandardScaler del modelo cancelación
#   modelo_knn_delay.pkl   → KNN entrenado para DELAYED_15
#   scaler_knn_delay.pkl   → StandardScaler del modelo retraso
#
# Archivos esperados en la carpeta models/ para la Red Neuronal:
#   modelo_mlp_cancel.pkl  → MLP entrenada para CANCELLED
#   scaler_mlp_cancel.pkl  → StandardScaler del modelo cancelación
#   modelo_mlp_delay.pkl   → MLP entrenada para DELAYED_15
#   scaler_mlp_delay.pkl   → StandardScaler del modelo retraso

def cargar_modelo(nombre_archivo):
    """Carga un .pkl desde la carpeta models/. Retorna None si no existe."""
    ruta = os.path.join(RUTA_MODELOS, nombre_archivo)
    if os.path.exists(ruta):
        return joblib.load(ruta)
    print(f"  Modelo no encontrado: {ruta}")
    return None

print("\n" + "=" * 50)
print("  SkyPredict — Backend Flask")
print("=" * 50)
print("\nCargando modelos...")

modelo_cancel  = cargar_modelo('modelo_knn_cancel.pkl')
scaler_cancel  = cargar_modelo('scaler_knn_cancel.pkl')
modelo_delay   = cargar_modelo('modelo_knn_delay.pkl')
scaler_delay   = cargar_modelo('scaler_knn_delay.pkl')

# Modelos MLP (Red Neuronal)
modelo_mlp_cancel  = cargar_modelo('modelo_mlp_cancel.pkl')
scaler_mlp_cancel  = cargar_modelo('scaler_mlp_cancel.pkl')
modelo_mlp_delay   = cargar_modelo('modelo_mlp_delay.pkl')
scaler_mlp_delay   = cargar_modelo('scaler_mlp_delay.pkl')

# LabelEncoders guardados por preprocessing.py
# Convierten strings ("TX", "Dallas/Fort Worth, TX") a los mismos
# enteros que usó el modelo durante el entrenamiento.
label_encoders = cargar_modelo('label_encoders.pkl')

# Resumen de carga
modelos_ok = all([modelo_cancel, scaler_cancel, modelo_delay, scaler_delay])
modelos_mlp_ok = all([modelo_mlp_cancel, scaler_mlp_cancel, modelo_mlp_delay, scaler_mlp_delay])
if modelos_ok:
    print("  Modelos KNN cargados correctamente")
else:
    print("  Modelos KNN no disponibles. Corre train_KNN.py primero.")
if modelos_mlp_ok:
    print("  Modelos MLP cargados correctamente")
else:
    print("  Modelos MLP no disponibles. Corre train_RED_NEURONAL.py primero.")

print(f"\n  http://localhost:5000")
print("=" * 50 + "\n")

# -------------------------------------------------------------
# Codificación de variables categóricas
# -------------------------------------------------------------
# El LabelEncoder en preprocessing.py asignó enteros así:
#   OP_UNIQUE_CARRIER: AA=0, DL=1, WN=2  (orden alfabético)
#   Estados y ciudades: orden alfabético de los valores únicos
#
# Para las ciudades y estados el frontend envía el string
# exacto (ej. "TX", "Dallas, TX") y debemos convertirlo
# al mismo entero que usó el modelo al entrenarse.
#
# Como no guardamos los LabelEncoders en preprocessing.py,
# usamos el mismo método hash que estaba antes para estados/ciudades
# → esto es un placeholder que deberán reemplazar cuando re-corran
#   preprocessing.py guardando los encoders con joblib.
#
# Para OP_UNIQUE_CARRIER sí tenemos el mapa exacto (solo 3 valores).

CARRIER_MAP = {'AA': 0, 'DL': 1, 'WN': 2}

def codificar_categoria(columna, valor):
    """
    Convierte un string al entero que le asignó el LabelEncoder durante el preprocesamiento. Si el valor no existe en el encoder
    (ciudad desconocida), devuelve 0 como fallback.
    Esto garantiza que el modelo reciba valores dentro del rango con el que fue entrenado (0 a N-1 clases).
    """
    if label_encoders is None:
        # Fallback si no se corrió preprocessing.py aún
        return abs(hash(str(valor).strip().upper())) % 10000
    le = label_encoders.get(columna)
    if le is None:
        return 0
    val_str = str(valor).strip()
    if val_str in le.classes_:
        return int(le.transform([val_str])[0])
    # Valor no visto durante entrenamiento → usar clase más cercana (0)
    return 0

def hhmm_a_minutos(valor_str):
    """
    Convierte 'HH:MM' (formato del input time en HTML) a minutos
    desde medianoche. Mismo formato que usa preprocessing.py.
    Ejemplos: '08:30' → 510,  '14:00' → 840,  '00:15' → 15
    """
    try:
        partes  = str(valor_str).split(':')
        horas   = int(partes[0])
        minutos = int(partes[1]) if len(partes) > 1 else 0
        return float(horas * 60 + minutos)
    except Exception:
        return 0.0

def preprocesar_entrada(datos):
    """
    Transforma el JSON del frontend al DataFrame que espera el modelo.

    El orden de columnas DEBE coincidir exactamente con el orden
    usado durante el entrenamiento en train_knn.py o train_RED_NEURONAL.py (variable FEATURES):
        YEAR, MONTH, DAY_OF_MONTH, DAY_OF_WEEK,
        OP_UNIQUE_CARRIER, CRS_DEP_TIME, CRS_ARR_TIME,
        ORIGIN_STATE_ABR, DEST_STATE_ABR,
        ORIGIN_CITY_NAME, DEST_CITY_NAME

    Parámetros recibidos del frontend (frontend.js → getFormData()):
        year, month, day, dow, carrier,
        depTime, arrTime,
        originState, destState,
        originCity, destCity
    """
    features = {
        'YEAR':              int(datos.get('year', 2019)),
        'MONTH':             int(datos.get('month', 1)),
        'DAY_OF_MONTH':      int(datos.get('day', 1)),
        'DAY_OF_WEEK':       int(datos.get('dow', 1)),
        'OP_UNIQUE_CARRIER': CARRIER_MAP.get(datos.get('carrier', 'WN'), 2),
        'CRS_DEP_TIME':      hhmm_a_minutos(datos.get('depTime', '08:00')),
        'CRS_ARR_TIME':      hhmm_a_minutos(datos.get('arrTime', '10:00')),
        'ORIGIN_STATE_ABR':  codificar_categoria('ORIGIN_STATE_ABR', datos.get('originState', '')),
        'DEST_STATE_ABR':    codificar_categoria('DEST_STATE_ABR',   datos.get('destState', '')),
        'ORIGIN_CITY_NAME':  codificar_categoria('ORIGIN_CITY_NAME', datos.get('originCity', '')),
        'DEST_CITY_NAME':    codificar_categoria('DEST_CITY_NAME',   datos.get('destCity', '')),
    }
    return pd.DataFrame([features])

# -------------------------------------------------------------
# GET / — Sirve el frontend
# -------------------------------------------------------------
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# -------------------------------------------------------------
# GET /<filename> — Sirve archivos estáticos (CSS, JS)
# -------------------------------------------------------------
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# -------------------------------------------------------------
# GET /api/status — Estado del servidor y modelos
# -------------------------------------------------------------
@app.route('/api/status')
def api_status():
    """
    Endpoint de diagnóstico. El frontend puede llamarlo para saber
    si los modelos están listos antes de dejar al usuario predecir.
    """
    return jsonify({
        'servidor':      'ok',
        'modelo_cancel': modelo_cancel is not None,
        'modelo_delay':  modelo_delay  is not None,
        'modelos_listos': modelos_ok
    })

# -------------------------------------------------------------
# GET /api/ciudades/<state>
# -------------------------------------------------------------
@app.route('/api/ciudades/<state>')
def get_ciudades(state):
    STATES_CITIES = {
        "AK": ["Anchorage, AK","Fairbanks, AK","Juneau, AK"],
        "AL": ["Birmingham, AL","Huntsville, AL","Mobile, AL"],
        "AR": ["Fayetteville, AR","Little Rock, AR"],
        "AZ": ["Phoenix, AZ","Tucson, AZ"],
        "CA": ["Burbank, CA","Fresno, CA","Long Beach, CA","Los Angeles, CA","Oakland, CA","Ontario, CA","Palm Springs, CA","Sacramento, CA","San Diego, CA","San Francisco, CA","San Jose, CA","Santa Ana, CA","Santa Barbara, CA"],
        "CO": ["Colorado Springs, CO","Denver, CO","Eagle, CO","Gunnison, CO","Hayden, CO","Montrose/Delta, CO"],
        "CT": ["Hartford, CT"],
        "FL": ["Daytona Beach, FL","Fort Lauderdale, FL","Fort Myers, FL","Gainesville, FL","Jacksonville, FL","Key West, FL","Melbourne, FL","Miami, FL","Orlando, FL","Panama City, FL","Pensacola, FL","Sarasota/Bradenton, FL","Tallahassee, FL","Tampa, FL","Valparaiso, FL","West Palm Beach/Palm Beach, FL"],
        "GA": ["Atlanta, GA","Augusta, GA","Savannah, GA"],
        "HI": ["Hilo, HI","Honolulu, HI","Kahului, HI","Kona, HI","Lihue, HI"],
        "IA": ["Cedar Rapids/Iowa City, IA","Des Moines, IA"],
        "ID": ["Boise, ID"],
        "IL": ["Bloomington/Normal, IL","Chicago, IL"],
        "IN": ["Evansville, IN","Indianapolis, IN","South Bend, IN"],
        "KS": ["Wichita, KS"],
        "KY": ["Cincinnati, KY","Lexington, KY","Louisville, KY"],
        "LA": ["Baton Rouge, LA","Lafayette, LA","New Orleans, LA","Shreveport, LA"],
        "MA": ["Boston, MA"],
        "MD": ["Baltimore, MD"],
        "ME": ["Bangor, ME","Portland, ME"],
        "MI": ["Detroit, MI","Flint, MI","Grand Rapids, MI","Lansing, MI","Traverse City, MI"],
        "MN": ["Duluth, MN","Minneapolis, MN"],
        "MO": ["Kansas City, MO","Springfield, MO","St. Louis, MO"],
        "MS": ["Gulfport/Biloxi, MS","Jackson/Vicksburg, MS"],
        "MT": ["Billings, MT","Bozeman, MT","Great Falls, MT","Kalispell, MT","Missoula, MT"],
        "NC": ["Asheville, NC","Charlotte, NC","Fayetteville, NC","Greensboro/High Point, NC","Jacksonville/Camp Lejeune, NC","Raleigh/Durham, NC","Wilmington, NC"],
        "ND": ["Bismarck/Mandan, ND","Fargo, ND","Minot, ND"],
        "NE": ["Omaha, NE"],
        "NH": ["Manchester, NH"],
        "NJ": ["Newark, NJ"],
        "NM": ["Albuquerque, NM"],
        "NV": ["Las Vegas, NV","Reno, NV"],
        "NY": ["Albany, NY","Buffalo, NY","Islip, NY","New York, NY","Rochester, NY","Syracuse, NY","White Plains, NY"],
        "OH": ["Akron, OH","Cleveland, OH","Columbus, OH","Dayton, OH"],
        "OK": ["Oklahoma City, OK","Tulsa, OK"],
        "OR": ["Portland, OR"],
        "PA": ["Allentown/Bethlehem/Easton, PA","Harrisburg, PA","Philadelphia, PA","Pittsburgh, PA","Scranton/Wilkes-Barre, PA"],
        "PR": ["San Juan, PR"],
        "RI": ["Providence, RI"],
        "SC": ["Charleston, SC","Columbia, SC","Greer, SC","Myrtle Beach, SC"],
        "SD": ["Rapid City, SD","Sioux Falls, SD"],
        "TN": ["Bristol/Johnson City/Kingsport, TN","Chattanooga, TN","Knoxville, TN","Memphis, TN","Nashville, TN"],
        "TX": ["Amarillo, TX","Austin, TX","Corpus Christi, TX","Dallas, TX","Dallas/Fort Worth, TX","El Paso, TX","Harlingen/San Benito, TX","Houston, TX","Lubbock, TX","Midland/Odessa, TX","Mission/McAllen/Edinburg, TX","San Antonio, TX"],
        "UT": ["Salt Lake City, UT"],
        "VA": ["Charlottesville, VA","Newport News/Williamsburg, VA","Norfolk, VA","Richmond, VA","Roanoke, VA","Washington, VA"],
        "VI": ["Charlotte Amalie, VI","Christiansted, VI"],
        "VT": ["Burlington, VT"],
        "WA": ["Pasco/Kennewick/Richland, WA","Seattle, WA","Spokane, WA"],
        "WI": ["Appleton, WI","Green Bay, WI","Madison, WI","Milwaukee, WI"],
        "WV": ["Charleston/Dunbar, WV"],
        "WY": ["Jackson, WY"],
    }
    ciudades = STATES_CITIES.get(state.upper(), [])
    return jsonify({'state': state.upper(), 'ciudades': ciudades})

# -------------------------------------------------------------
# POST /predict/cancel — Predicción de cancelación
# -------------------------------------------------------------
@app.route('/predict/cancel', methods=['POST'])
def predict_cancel():
    """
    Recibe el JSON del frontend, preprocesa los datos y devuelve la predicción del modelo de cancelación.
    Si el modelo no está cargado (no se corrió train_knn.py), devuelve error 503 con mensaje claro.
    """
    # Verificar que el modelo está disponible
    if modelo_cancel is None or scaler_cancel is None:
        return jsonify({
            'error': 'Modelo no disponible. Ejecuta train_knn.py primero.'
        }), 503

    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400

        # 1. Preprocesar entrada del formulario
        X = preprocesar_entrada(datos)

        # 2. Escalar con el scaler entrenado para cancelación
        #    IMPORTANTE: usar scaler_cancel (ajustado sobre datos de cancelación),
        #    NO scaler_delay, porque fueron ajustados sobre datasets diferentes.
        X_scaled = scaler_cancel.transform(X)

        # 3. Predecir
        #    predict_proba devuelve [prob_clase_0, prob_clase_1]
        #    Tomamos el índice 1 = probabilidad de que sea cancelado
        prob = float(modelo_cancel.predict_proba(X_scaled)[0][1])
        pred = int(modelo_cancel.predict(X_scaled)[0])

        return jsonify({
            'prediccion':   pred,
            'probabilidad': round(prob, 4),
            'etiqueta':     'Cancelado' if pred == 1 else 'No cancelado',
            'modelo':       'KNN — Cancelación'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# POST /predict/delay — Predicción de retraso >= 15 min
# -------------------------------------------------------------
@app.route('/predict/delay', methods=['POST'])
def predict_delay():
    """
    Recibe el JSON del frontend, preprocesa los datos y devuelve
    la predicción del modelo KNN de retraso significativo.

    Este modelo solo aplica a vuelos no cancelados. El usuario
    que llega a este formulario ya eligió "retraso", así que
    asumimos que el vuelo no está cancelado.
    """
    if modelo_delay is None or scaler_delay is None:
        return jsonify({
            'error': 'Modelo no disponible. Ejecuta train_knn.py primero.'
        }), 503

    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400

        # 1. Preprocesar
        X = preprocesar_entrada(datos)

        # 2. Escalar con el scaler de retraso (ajustado sobre vuelos no cancelados)
        X_scaled = scaler_delay.transform(X)

        # 3. Predecir
        prob = float(modelo_delay.predict_proba(X_scaled)[0][1])
        pred = int(modelo_delay.predict(X_scaled)[0])

        return jsonify({
            'prediccion':   pred,
            'probabilidad': round(prob, 4),
            'etiqueta':     'Retraso ≥ 15 min' if pred == 1 else 'Llegada a tiempo',
            'modelo':       'KNN — Retraso'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# Función reutilizable para predecir con cualquier modelo
# -------------------------------------------------------------
def predecir(modelo, scaler, datos, nombre_modelo):
    """Preprocesa, escala y predice. Retorna dict con resultado."""
    X        = preprocesar_entrada(datos)
    X_scaled = scaler.transform(X)
    prob     = float(modelo.predict_proba(X_scaled)[0][1])
    pred     = int(modelo.predict(X_scaled)[0])
    return {
        'prediccion':   pred,
        'probabilidad': round(prob, 4),
        'modelo':       nombre_modelo
    }

# -------------------------------------------------------------
# POST /predict/cancel/knn — KNN cancelación
# -------------------------------------------------------------
@app.route('/predict/cancel/knn', methods=['POST'])
def predict_cancel_knn():
    if modelo_cancel is None or scaler_cancel is None:
        return jsonify({'error': 'Modelo KNN cancelación no disponible'}), 503
    try:
        datos = request.get_json()
        res   = predecir(modelo_cancel, scaler_cancel, datos, 'KNN')
        res['etiqueta'] = 'Cancelado' if res['prediccion'] == 1 else 'No cancelado'
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# POST /predict/cancel/mlp — MLP cancelación
# -------------------------------------------------------------
@app.route('/predict/cancel/mlp', methods=['POST'])
def predict_cancel_mlp():
    if modelo_mlp_cancel is None or scaler_mlp_cancel is None:
        return jsonify({'error': 'Modelo MLP cancelación no disponible'}), 503
    try:
        datos = request.get_json()
        res   = predecir(modelo_mlp_cancel, scaler_mlp_cancel, datos, 'MLP')
        res['etiqueta'] = 'Cancelado' if res['prediccion'] == 1 else 'No cancelado'
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# POST /predict/delay/knn — KNN retraso
# -------------------------------------------------------------
@app.route('/predict/delay/knn', methods=['POST'])
def predict_delay_knn():
    if modelo_delay is None or scaler_delay is None:
        return jsonify({'error': 'Modelo KNN retraso no disponible'}), 503
    try:
        datos = request.get_json()
        res   = predecir(modelo_delay, scaler_delay, datos, 'KNN')
        res['etiqueta'] = 'Retraso ≥ 15 min' if res['prediccion'] == 1 else 'Llegada a tiempo'
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# POST /predict/delay/mlp — MLP retraso
# -------------------------------------------------------------
@app.route('/predict/delay/mlp', methods=['POST'])
def predict_delay_mlp():
    if modelo_mlp_delay is None or scaler_mlp_delay is None:
        return jsonify({'error': 'Modelo MLP retraso no disponible'}), 503
    try:
        datos = request.get_json()
        res   = predecir(modelo_mlp_delay, scaler_mlp_delay, datos, 'MLP')
        res['etiqueta'] = 'Retraso ≥ 15 min' if res['prediccion'] == 1 else 'Llegada a tiempo'
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# Punto de entrada
# -------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
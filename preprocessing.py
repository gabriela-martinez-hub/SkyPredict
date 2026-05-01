# ===========================================================================================================================
# Proyecto: SkyPredict — Sistema Web de Predicción de Vuelos
# Descripción: Limpieza y transformación del dataset de vuelos filtrado a las 3 aerolíneas principales (WN, DL, AA)
# ===========================================================================================================================

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os

# -------------------------------------------------------------
# PASO 1 — Cargar el dataset ya filtrado (WN, DL, AA)
# -------------------------------------------------------------

RUTA_ENTRADA = 'flights_top3.csv'
RUTA_SALIDA  = 'flights_processed.csv'

print("=" * 60)
print("PREPROCESAMIENTO DE DATOS — SkyPredict")
print("=" * 60)

df = pd.read_csv(RUTA_ENTRADA)
print(f"\n[1] Dataset cargado: {df.shape[0]:,} filas | {df.shape[1]} columnas")
print(f"    Aerolíneas presentes: {df['OP_UNIQUE_CARRIER'].unique().tolist()}")

# -------------------------------------------------------------
# PASO 2 — Crear DELAYED_15 ANTES de eliminar ARR_DELAY_NEW
# -------------------------------------------------------------
# DELAYED_15 es la variable objetivo del modelo de retraso.
# Un vuelo se considera con retraso significativo si llega
# 15 o más minutos tarde respecto a la hora programada.
# Solo aplica a vuelos NO cancelados (los cancelados no tienen
# ARR_DELAY_NEW registrado).
#
# Valores:
#   0 = Sin retraso significativo (llegó a tiempo o < 15 min tarde)
#   1 = Retraso significativo (llegó 15 o más minutos tarde)

df['DELAYED_15'] = (df['ARR_DELAY_NEW'] >= 15).astype(int)

total_operados = df[df['CANCELLED'] == 0].shape[0]
total_delayed  = df['DELAYED_15'].sum()
print(f"\n[2] Variable DELAYED_15 creada:")
print(f"    Sin retraso (0): {total_operados - total_delayed:,}")
print(f"    Con retraso (1): {total_delayed:,}")

# -------------------------------------------------------------
# PASO 3 — Eliminar columnas innecesarias
# -------------------------------------------------------------
# Columnas eliminadas y razón:
#
#   ARR_DELAY_NEW     → Ya fue usada para crear DELAYED_15.
#                       No puede ser entrada del modelo porque
#                       solo existe DESPUÉS de que el vuelo aterrizó.
#
#   AIR_TIME          → Tiempo real en el aire. También es un dato
#                       que solo se conoce después del vuelo,
#                       no al momento de predecir.
#
#   CANCELLATION_CODE → 97.87% de valores nulos (solo aplica a
#                       vuelos cancelados). No aporta como feature.
#
#   DISTANCE          → Para los modelos de cancelación y retraso
#                       lo relevante es el tiempo programado, no
#                       la distancia en millas.
#
#   DEP_DELAY_NEW     → Este vendría siendo el retraso real en la salida, sin embargo
#                       estamos enfocandonos en las variables programadas (CRS_DEP_TIME, CRS_ARR_TIME)
#                       para que el modelo pueda predecir antes de que el vuelo despegue.
#                       Estamos mirando el problema desde la perspectiva de un pasajero 
#                       que quiere saber si su vuelo se retrasará o cancelará antes de ir al aeropuerto.

columnas_eliminar = ['ARR_DELAY_NEW', 'AIR_TIME', 'CANCELLATION_CODE', 'DISTANCE', 'DEP_DELAY_NEW']
df.drop(columns=columnas_eliminar, inplace=True)
print(f"\n[3] Columnas eliminadas: {columnas_eliminar}")
print(f"    Columnas restantes: {df.shape[1]}")

# -------------------------------------------------------------
# PASO 4 — Imputar nulos en CRS_DEP_TIME y CRS_ARR_TIME
# -------------------------------------------------------------
# CRS_DEP_TIME: 5.782 nulos (0.02%) — muy pocos, imputamos con mediana
# CRS_ARR_TIME: 102.116 nulos (0.28%) — pocos, imputamos con mediana
#
# La mediana es más robusta que la media ante valores extremos
# (vuelos de madrugada vs vuelos al mediodía).

for col in ['CRS_DEP_TIME', 'CRS_ARR_TIME']:
    nulos_antes = df[col].isnull().sum()
    mediana = df[col].median()
    df[col].fillna(mediana, inplace=True)
    print(f"\n[4] {col}: {nulos_antes:,} nulos imputados con mediana ({mediana})")

# -------------------------------------------------------------
# PASO 5 — Convertir CRS_DEP_TIME y CRS_ARR_TIME a float (minutos)
# -------------------------------------------------------------
# El dataset almacena las horas en formato HHMM como número entero.
# Ejemplo: 1430 = 14:30 = 14*60 + 30 = 870 minutos desde medianoche
#
# Convertimos a minutos totales desde medianoche para que el modelo
# pueda interpretar la hora como un valor numérico continuo.
#
# Fórmula: minutos = (HHMM // 100) * 60 + (HHMM % 100)
# Ejemplo: 1430 → (1430 // 100) * 60 + (1430 % 100) = 14*60 + 30 = 870

def hhmm_a_minutos(valor):
    valor = int(valor)
    horas   = valor // 100
    minutos = valor % 100
    return horas * 60 + minutos

df['CRS_DEP_TIME'] = df['CRS_DEP_TIME'].apply(hhmm_a_minutos).astype(float)
df['CRS_ARR_TIME'] = df['CRS_ARR_TIME'].apply(hhmm_a_minutos).astype(float)

print(f"\n[5] CRS_DEP_TIME convertida a minutos. Rango: {df['CRS_DEP_TIME'].min():.0f} – {df['CRS_DEP_TIME'].max():.0f} min")
print(f"    CRS_ARR_TIME convertida a minutos. Rango: {df['CRS_ARR_TIME'].min():.0f} – {df['CRS_ARR_TIME'].max():.0f} min")

# -------------------------------------------------------------
# PASO 6 — Eliminar filas con nulos en DEP_DELAY_NEW
# -------------------------------------------------------------
# DEP_DELAY_NEW tiene nulos en vuelos cancelados (2.09%).
# Estos registros no tienen retraso de salida registrado,
# por lo tanto no son útiles como features de entrada.
# Se eliminan para mantener la integridad del dataset.

filas_antes = df.shape[0]
df.dropna(subset=['DEP_DELAY_NEW'], inplace=True)
filas_eliminadas = filas_antes - df.shape[0]
print(f"\n[6] Filas eliminadas por nulos en DEP_DELAY_NEW: {filas_eliminadas:,}")
print(f"    Filas restantes: {df.shape[0]:,}")

# -------------------------------------------------------------
# PASO 7 — Codificación de variables categóricas (Label Encoding)
# -------------------------------------------------------------
# Las variables de tipo string no pueden ser procesadas directamente
# por los modelos de ML. Se convierten a enteros mediante Label Encoding,
# que asigna un número único a cada categoría.
#
# Tabla de codificación:
#
# OP_UNIQUE_CARRIER (aerolínea):
#   AA → 0  |  DL → 1  |  WN → 2
#   (orden alfabético asignado por LabelEncoder)
#
# ORIGIN_STATE_ABR / DEST_STATE_ABR (estado, abreviatura 2 letras):
#   Cada estado de EE.UU. recibe un entero único.
#   Ejemplo: AL→0, AK→1, AZ→2, CA→5, FL→9, TX→43, ...
#
# ORIGIN_CITY_NAME / DEST_CITY_NAME (ciudad):
#   Cada ciudad recibe un entero único.
#   Ejemplo: "Atlanta, GA"→0, "Dallas, TX"→1, ...
#
# Nota: El LabelEncoder se ajusta (fit) con los datos de entrenamiento.
#       Los mapeos exactos dependen de los valores presentes en el dataset.

columnas_categoricas = [
    'OP_UNIQUE_CARRIER',
    'ORIGIN_STATE_ABR',
    'DEST_STATE_ABR',
    'ORIGIN_CITY_NAME',
    'DEST_CITY_NAME'
]

encoders = {}   # guardamos los encoders para usarlos luego en la API

print(f"\n[7] Codificación Label Encoding de variables categóricas:")
for col in columnas_categoricas:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
    print(f"    {col}: {len(le.classes_)} categorías únicas → enteros 0 a {len(le.classes_)-1}")

# -------------------------------------------------------------
# PASO 8 — Verificación final del dataset procesado
# -------------------------------------------------------------
print(f"\n[8] Verificación final:")
print(f"    Forma del dataset: {df.shape[0]:,} filas × {df.shape[1]} columnas")
print(f"    Nulos restantes: {df.isnull().sum().sum()}")
print(f"\n    Columnas finales:")

roles = {
    'YEAR':             'Feature temporal',
    'MONTH':            'Feature temporal',
    'DAY_OF_MONTH':     'Feature temporal',
    'DAY_OF_WEEK':      'Feature temporal',
    'OP_UNIQUE_CARRIER':'Feature codificada (aerolínea)',
    'CRS_DEP_TIME':     'Feature numérica (minutos desde medianoche)',
    'CRS_ARR_TIME':     'Feature numérica (minutos desde medianoche)',
    'DEP_DELAY_NEW':    'Feature numérica (minutos de retraso en salida)',
    'ORIGIN_STATE_ABR': 'Feature codificada (estado origen)',
    'DEST_STATE_ABR':   'Feature codificada (estado destino)',
    'ORIGIN_CITY_NAME': 'Feature codificada (ciudad origen)',
    'DEST_CITY_NAME':   'Feature codificada (ciudad destino)',
    'CANCELLED':        '🎯 TARGET — Modelo 1: Cancelación de vuelo',
    'DELAYED_15':       '🎯 TARGET — Modelo 2: Retraso ≥ 15 min',
}

for col in df.columns:
    print(f"    {col:<22} → {roles.get(col, 'Feature')}")

# -------------------------------------------------------------
# PASO 9 — Guardar dataset procesado
# -------------------------------------------------------------
df.to_csv(RUTA_SALIDA, index=False)
print(f"\n[9] Dataset guardado como: {RUTA_SALIDA}")
print("\n✅ Preprocesamiento completado.")

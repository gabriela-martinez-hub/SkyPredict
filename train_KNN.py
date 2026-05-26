# ==============================================================
# Proyecto: SkyPredict — Entrenamiento Modelo KNN
# Descripción: Entrena dos clasificadores KNN:
#   - Modelo 1: Predicción de CANCELACIÓN  → target: CANCELLED
#   - Modelo 2: Predicción de RETRASO      → target: DELAYED_15
#
# Columnas de entrada (features):
#   YEAR, MONTH, DAY_OF_MONTH, DAY_OF_WEEK,
#   OP_UNIQUE_CARRIER, CRS_DEP_TIME, CRS_ARR_TIME,
#   ORIGIN_STATE_ABR, DEST_STATE_ABR,
#   ORIGIN_CITY_NAME, DEST_CITY_NAME
#
# Nota sobre los targets:
#   CANCELLED  → existía en el dataset original (1=cancelado, 0=no)
#   DELAYED_15 → variable derivada creada en preprocessing.py
#                (1 si ARR_DELAY_NEW >= 15, solo en vuelos no cancelados)
#
# Entradas:  flights_processed.csv
# Salidas:   models/modelo_knn_cancel.pkl
#            models/modelo_knn_delay.pkl
#            models/scaler_knn.pkl
# ==============================================================

import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
import os

# --------------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------------
RUTA_DATOS   = 'flights_processed.csv'
RUTA_MODELOS = 'models'
os.makedirs(RUTA_MODELOS, exist_ok=True)

FEATURES = [
    'YEAR', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK',
    'OP_UNIQUE_CARRIER',
    'CRS_DEP_TIME', 'CRS_ARR_TIME',
    'ORIGIN_STATE_ABR', 'DEST_STATE_ABR',
    'ORIGIN_CITY_NAME', 'DEST_CITY_NAME'
]

print("=" * 60)
print("  ENTRENAMIENTO KNN — SkyPredict")
print("=" * 60)

# --------------------------------------------------------------
# PASO 1 — Cargar datos
# --------------------------------------------------------------
print("\n[1] Cargando datos...")
df = pd.read_csv(RUTA_DATOS)
# df = df.sample(n=500_000, random_state=42)  # descomenta si es muy lento
print(f"    Filas cargadas : {df.shape[0]:,}")
print(f"    Columnas       : {df.shape[1]}")
print(f"    Columnas finales: {df.columns.tolist()}")

# Guardar info de encoders para que app.py valide entradas
COLS_CATEGORICAS = ['OP_UNIQUE_CARRIER','ORIGIN_STATE_ABR','DEST_STATE_ABR',
                    'ORIGIN_CITY_NAME','DEST_CITY_NAME']
encoders_info = {}
for col in COLS_CATEGORICAS:
    encoders_info[col] = {
        'min': int(df[col].min()),
        'max': int(df[col].max()),
        'n_clases': int(df[col].nunique())
    }
    print(f"    {col}: {encoders_info[col]['n_clases']} clases únicas "
          f"(rango {encoders_info[col]['min']}–{encoders_info[col]['max']})")
joblib.dump(encoders_info, os.path.join(RUTA_MODELOS, 'encoders_info.pkl'))
print("    models/encoders_info.pkl guardado")

# --------------------------------------------------------------
# PASO 2 — Preparar datos Modelo CANCELACIÓN
# --------------------------------------------------------------
print("\n[2] Preparando datos — Modelo CANCELACIÓN...")
df_cancel = df[FEATURES + ['CANCELLED']].dropna()
X_cancel  = df_cancel[FEATURES]
y_cancel  = df_cancel['CANCELLED']
print(f"    Total filas     : {df_cancel.shape[0]:,}")
print(f"    No cancelados(0): {(y_cancel==0).sum():,}  ({(y_cancel==0).mean()*100:.1f}%)")
print(f"    Cancelados   (1): {(y_cancel==1).sum():,}  ({(y_cancel==1).mean()*100:.1f}%)")

# --------------------------------------------------------------
# PASO 3 — Preparar datos Modelo RETRASO
# --------------------------------------------------------------
# Solo vuelos NO cancelados: DELAYED_15 no aplica a cancelados
print("\n[3] Preparando datos — Modelo RETRASO...")
df_delay = df[df['CANCELLED'] == 0][FEATURES + ['DELAYED_15']].dropna()
X_delay  = df_delay[FEATURES]
y_delay  = df_delay['DELAYED_15']
print(f"    Total filas (no cancelados): {df_delay.shape[0]:,}")
print(f"    A tiempo     (0): {(y_delay==0).sum():,}  ({(y_delay==0).mean()*100:.1f}%)")
print(f"    Retrasados   (1): {(y_delay==1).sum():,}  ({(y_delay==1).mean()*100:.1f}%)")

# --------------------------------------------------------------
# PASO 4 — Dividir train/test (80% / 20%)
# --------------------------------------------------------------
print("\n[4] Dividiendo en train/test (80/20)...")
X_cancel_train, X_cancel_test, y_cancel_train, y_cancel_test = train_test_split(
    X_cancel, y_cancel, test_size=0.2, random_state=42, stratify=y_cancel)
X_delay_train, X_delay_test, y_delay_train, y_delay_test = train_test_split(
    X_delay, y_delay, test_size=0.2, random_state=42, stratify=y_delay)
print(f"    Cancelación → Train: {X_cancel_train.shape[0]:,} | Test: {X_cancel_test.shape[0]:,}")
print(f"    Retraso     → Train: {X_delay_train.shape[0]:,}  | Test: {X_delay_test.shape[0]:,}")

# --------------------------------------------------------------
# PASO 5 — Escalar features
# --------------------------------------------------------------
print("\n[5] Escalando features...")
scaler_cancel = StandardScaler()
X_cancel_train_s = scaler_cancel.fit_transform(X_cancel_train)
X_cancel_test_s  = scaler_cancel.transform(X_cancel_test)

scaler_delay = StandardScaler()
X_delay_train_s = scaler_delay.fit_transform(X_delay_train)
X_delay_test_s  = scaler_delay.transform(X_delay_test)
print("    Escalado completado.")

# --------------------------------------------------------------
# PASO 6 — Parámetros KNN
# --------------------------------------------------------------
# weights='distance': vecinos más cercanos pesan más en la votación.
# Esto mejora el rendimiento con clases desbalanceadas porque los
# pocos ejemplos de la clase minoritaria que son realmente similares
# tienen mayor influencia.
# n_neighbors=7: K más alto reduce sobreajuste (overfitting).
KNN_PARAMS = dict(
    n_neighbors=7,
    weights='distance',
    algorithm='auto',
    metric='minkowski',
    p=2,
    n_jobs=-1
)

# --------------------------------------------------------------
# PASO 7 — Undersampling para manejar desbalanceo
# --------------------------------------------------------------
# Problema: 98.1% clase 0 vs 1.9% clase 1 en cancelación.
# El modelo tiende a predecir siempre "No cancelado" porque
# así acierta el 98% del tiempo sin aprender nada útil.
#
# Solución — Undersampling de la clase mayoritaria:
# Reducimos la clase 0 a un múltiplo razonable de la clase 1.
# Cancelación: ratio 5:1 (0 tiene 5x más ejemplos que 1)
# Retraso:     ratio 3:1 (0 tiene 3x más ejemplos que 1)
# Esto obliga al modelo a aprender patrones de ambas clases.
#
# IMPORTANTE: el undersampling se aplica SOLO al train,
# nunca al test (el test debe reflejar la realidad).

print("\n[6] Aplicando undersampling al train...")

def undersample(X_scaled, y, ratio, seed=42):
    """Reduce clase mayoritaria a ratio * tamaño clase minoritaria."""
    df_tmp = pd.DataFrame(X_scaled, columns=FEATURES)
    df_tmp['target'] = y.values if hasattr(y, 'values') else y
    n_min = (df_tmp['target'] == 1).sum()
    df_may = df_tmp[df_tmp['target'] == 0].sample(n=n_min * ratio, random_state=seed)
    df_min = df_tmp[df_tmp['target'] == 1]
    df_bal = pd.concat([df_may, df_min]).sample(frac=1, random_state=seed)
    return df_bal[FEATURES].values, df_bal['target'].values

X_cancel_bal, y_cancel_bal = undersample(X_cancel_train_s, y_cancel_train, ratio=5)
X_delay_bal,  y_delay_bal  = undersample(X_delay_train_s,  y_delay_train,  ratio=3)

print(f"    Cancelación balanceado → 0: {(y_cancel_bal==0).sum():,} | 1: {(y_cancel_bal==1).sum():,}")
print(f"    Retraso balanceado     → 0: {(y_delay_bal==0).sum():,}  | 1: {(y_delay_bal==1).sum():,}")

# --------------------------------------------------------------
# PASO 8A — Entrenar Modelo CANCELACIÓN
# --------------------------------------------------------------
print("\n[7] Entrenando KNN — Modelo CANCELACIÓN...")
knn_cancel = KNeighborsClassifier(**KNN_PARAMS)
knn_cancel.fit(X_cancel_bal, y_cancel_bal)

# Evaluar sobre el TEST ORIGINAL (sin balancear) — refleja la realidad
y_cancel_pred = knn_cancel.predict(X_cancel_test_s)

print("\n    ── Métricas Modelo CANCELACIÓN ──")
print(f"    Accuracy : {accuracy_score(y_cancel_test, y_cancel_pred):.4f}")
print(f"    Precision: {precision_score(y_cancel_test, y_cancel_pred, zero_division=0):.4f}")
print(f"    Recall   : {recall_score(y_cancel_test, y_cancel_pred, zero_division=0):.4f}")
print(f"    F1-Score : {f1_score(y_cancel_test, y_cancel_pred, zero_division=0):.4f}")
print()
print(classification_report(y_cancel_test, y_cancel_pred,
      target_names=['No cancelado (0)', 'Cancelado (1)'], zero_division=0))
cm = confusion_matrix(y_cancel_test, y_cancel_pred)
print(f"    Matriz de confusión:")
print(f"    [[VN={cm[0,0]:,}  FP={cm[0,1]:,}]")
print(f"     [FN={cm[1,0]:,}  VP={cm[1,1]:,}]]")
print("     VN=Verdadero Negativo, FP=Falso Positivo")
print("     FN=Falso Negativo,     VP=Verdadero Positivo")

# --------------------------------------------------------------
# PASO 8B — Entrenar Modelo RETRASO
# --------------------------------------------------------------
print("\n[8] Entrenando KNN — Modelo RETRASO ≥ 15 min...")
knn_delay = KNeighborsClassifier(**KNN_PARAMS)
knn_delay.fit(X_delay_bal, y_delay_bal)

y_delay_pred = knn_delay.predict(X_delay_test_s)

print("\n    ── Métricas Modelo RETRASO ──")
print(f"    Accuracy : {accuracy_score(y_delay_test, y_delay_pred):.4f}")
print(f"    Precision: {precision_score(y_delay_test, y_delay_pred, zero_division=0):.4f}")
print(f"    Recall   : {recall_score(y_delay_test, y_delay_pred, zero_division=0):.4f}")
print(f"    F1-Score : {f1_score(y_delay_test, y_delay_pred, zero_division=0):.4f}")
print()
print(classification_report(y_delay_test, y_delay_pred,
      target_names=['A tiempo (0)', 'Retraso ≥15min (1)'], zero_division=0))
cm_d = confusion_matrix(y_delay_test, y_delay_pred)
print(f"    Matriz de confusión:")
print(f"    [[VN={cm_d[0,0]:,}  FP={cm_d[0,1]:,}]")
print(f"     [FN={cm_d[1,0]:,}  VP={cm_d[1,1]:,}]]")

# --------------------------------------------------------------
# PASO 9 — Guardar modelos y scalers
# --------------------------------------------------------------
print("\n[9] Guardando modelos y scalers...")
joblib.dump(knn_cancel,    os.path.join(RUTA_MODELOS, 'modelo_knn_cancel.pkl'))
joblib.dump(scaler_cancel, os.path.join(RUTA_MODELOS, 'scaler_knn_cancel.pkl'))
joblib.dump(knn_delay,     os.path.join(RUTA_MODELOS, 'modelo_knn_delay.pkl'))
joblib.dump(scaler_delay,  os.path.join(RUTA_MODELOS, 'scaler_knn_delay.pkl'))
print("    models/modelo_knn_cancel.pkl")
print("    models/scaler_knn_cancel.pkl")
print("    models/modelo_knn_delay.pkl")
print("    models/scaler_knn_delay.pkl")
print("\nEntrenamiento KNN completado.")
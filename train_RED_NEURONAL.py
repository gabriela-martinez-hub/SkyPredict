# -*- coding: utf-8 -*-
"""Entrenamiento Red Neuronal — SkyPredict

Targets:
    CANCELLED  → Modelo 1: predice si un vuelo será cancelado
    DELAYED_15 → Modelo 2: predice si un vuelo llegará con >= 15 min de retraso
                 (solo aplica a vuelos NO cancelados)
"""

#Importar librerias
from sklearn.neural_network import MLPClassifier  #Dependencia que ya trae modelos de inteligencia artificial
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score,
    classification_report,
    confusion_matrix
)
import joblib  #Guarda los pesos que minimizan el margen de error y los descarga
import pandas as pd
import os

os.makedirs('models', exist_ok=True)

#Columnas de entrada del modelo (variables finales tras preprocessing.py)
#Se eliminaron: ARR_DELAY_NEW, DEP_DELAY_NEW, AIR_TIME, CANCELLATION_CODE, DISTANCE
FEATURES = [
    'YEAR', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK',
    'OP_UNIQUE_CARRIER',
    'CRS_DEP_TIME', 'CRS_ARR_TIME',
    'ORIGIN_STATE_ABR', 'DEST_STATE_ABR',
    'ORIGIN_CITY_NAME', 'DEST_CITY_NAME'
]

print("=" * 60)
print("  ENTRENAMIENTO RED NEURONAL (MLP) — SkyPredict")
print("=" * 60)

# ==============================================================
# MODELO 1 — CANCELACIÓN DE VUELO
# ==============================================================

#Cargar datos — reemplaza load_iris() del ejemplo de clase
#flights_processed.csv fue generado por preprocessing.py
df = pd.read_csv('flights_processed.csv')
# df = df.sample(n=500_000, random_state=42)  # descomenta si es muy lento

#Separar features y target CANCELLED
#En clase: X, y = load_iris(return_X_y=True)
#Aqui: X son las columnas de entrada, y es la columna CANCELLED
df_cancel = df[FEATURES + ['CANCELLED']].dropna()
X = df_cancel[FEATURES]
y = df_cancel['CANCELLED']

print(f"\n[Cancelación] Total filas: {df_cancel.shape[0]:,}")
print(f"    No cancelados (0): {(y==0).sum():,}  ({(y==0).mean()*100:.1f}%)")
print(f"    Cancelados    (1): {(y==1).sum():,}  ({(y==1).mean()*100:.1f}%)")

#Dividir el dataset en entrenamiento y prueba
#stratify=y mantiene la proporcion de clases en train y test
#importante con datos desbalanceados (98.1% vs 1.9%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

#Undersampling — manejo del desbalanceo de clases
#Problema: 98.1% clase 0 vs 1.9% clase 1. Sin esto el modelo
#predice siempre "No cancelado" y tiene 98% accuracy sin aprender nada.
#Solucion: reducir clase 0 a 5x el tamaño de clase 1 solo en el TRAIN.
#El TEST no se modifica — debe reflejar la distribucion real.
df_tr = pd.DataFrame(X_train, columns=FEATURES)
df_tr['target'] = y_train.values
n_min   = (df_tr['target'] == 1).sum()
df_may  = df_tr[df_tr['target'] == 0].sample(n=n_min * 5, random_state=42)
df_min  = df_tr[df_tr['target'] == 1]
df_bal  = pd.concat([df_may, df_min]).sample(frac=1, random_state=42)
X_train_bal = df_bal[FEATURES].values
y_train_bal = df_bal['target'].values
print(f"\n    Train balanceado → 0: {(y_train_bal==0).sum():,} | 1: {(y_train_bal==1).sum():,}")

#Aqui vamos a transformar los valores — Escalar features
scaler_cancel = StandardScaler()  #Transformar los datos de X_train y de X_test
X_train_bal   = scaler_cancel.fit_transform(X_train_bal)  #.fit utiliza medidas estadisticas y busca la manera de estandarizar
X_test_s      = scaler_cancel.transform(X_test)           #Solo me interesa que queden en la misma escala

#Definir la red neuronal — mismos parametros del ejemplo de clase
model_cancel = MLPClassifier(
    hidden_layer_sizes=(64, 32),  #Se considero tener dos capas ocultas en la red neuronal
    activation='relu',            #Funcion de activacion: devuelve max(0, x)
    solver='adam',                #Optimiza el proceso para optimizar las operaciones
    alpha=0.001,                  #Penaliza los pesos de las redes neuronales cuando eran muy bajos
    learning_rate_init=0.001,     #La tasa de aprendizaje o constante de aprendizaje
    max_iter=500,                 #Cantidad de iteraciones, tener cuidado para que no se sobre entrene
    early_stopping=True,          #Para antes de tiempo cuando el valor del error no cambia
    validation_fraction=0.1,      #10% del train se usa para validar en cada epoca
    n_iter_no_change=10,          #Detiene si no mejora en 10 epocas consecutivas
    random_state=42               #Genere la misma reproduccion
)

#AQUI YA TENEMOS EL MODELO ENTRENADO
print("\n[Cancelación] Entrenando red neuronal... (puede tardar varios minutos)")

#Entrenar
model_cancel.fit(X_train_bal, y_train_bal)
print(f"    Epocas entrenadas: {model_cancel.n_iter_}")
print(f"    Loss final       : {model_cancel.loss_:.4f}")

#Evaluar — sobre el TEST ORIGINAL sin balancear (refleja la realidad)
y_pred_cancel = model_cancel.predict(X_test_s)
print(f"\n    Accuracy : {accuracy_score(y_test, y_pred_cancel):.4f}")
print(f"    Precision: {precision_score(y_test, y_pred_cancel, zero_division=0):.4f}")
print(f"    Recall   : {recall_score(y_test, y_pred_cancel, zero_division=0):.4f}")
print(f"    F1-Score : {f1_score(y_test, y_pred_cancel, zero_division=0):.4f}")
print()
print(classification_report(y_test, y_pred_cancel,
      target_names=['No cancelado', 'Cancelado'], zero_division=0))
cm = confusion_matrix(y_test, y_pred_cancel)
print(f"    Matriz de confusion:")
print(f"    [[VN={cm[0,0]:,}  FP={cm[0,1]:,}]")
print(f"     [FN={cm[1,0]:,}  VP={cm[1,1]:,}]]")

#Guardar modelo y scaler
joblib.dump(model_cancel,  'models/modelo_mlp_cancel.pkl')
joblib.dump(scaler_cancel, 'models/scaler_mlp_cancel.pkl')
print('\nModelo cancelacion guardado correctamente')

# ==============================================================
# MODELO 2 — RETRASO SIGNIFICATIVO (>= 15 min)
# ==============================================================

#Cargar datos — solo vuelos NO cancelados
#DELAYED_15 fue creada en preprocessing.py: 1 si ARR_DELAY_NEW >= 15
#Solo aplica a vuelos que efectivamente despegaron (CANCELLED == 0)
df_delay = df[df['CANCELLED'] == 0][FEATURES + ['DELAYED_15']].dropna()
X = df_delay[FEATURES]
y = df_delay['DELAYED_15']

print(f"\n[Retraso] Total filas (no cancelados): {df_delay.shape[0]:,}")
print(f"    A tiempo    (0): {(y==0).sum():,}  ({(y==0).mean()*100:.1f}%)")
print(f"    Retrasados  (1): {(y==1).sum():,}  ({(y==1).mean()*100:.1f}%)")

#Dividir el dataset en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

#Undersampling — ratio 3:1 para retraso (83.5% vs 16.5%)
df_tr2  = pd.DataFrame(X_train, columns=FEATURES)
df_tr2['target'] = y_train.values
n_min2   = (df_tr2['target'] == 1).sum()
df_may2  = df_tr2[df_tr2['target'] == 0].sample(n=n_min2 * 3, random_state=42)
df_min2  = df_tr2[df_tr2['target'] == 1]
df_bal2  = pd.concat([df_may2, df_min2]).sample(frac=1, random_state=42)
X_train_bal2 = df_bal2[FEATURES].values
y_train_bal2 = df_bal2['target'].values
print(f"\n    Train balanceado → 0: {(y_train_bal2==0).sum():,} | 1: {(y_train_bal2==1).sum():,}")

#Aqui vamos a transformar los valores — Escalar features
scaler_delay  = StandardScaler()
X_train_bal2  = scaler_delay.fit_transform(X_train_bal2)
X_test_s2     = scaler_delay.transform(X_test)

#Definir la red neuronal — mismos parametros
model_delay = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',
    alpha=0.001,
    learning_rate_init=0.001,
    max_iter=500,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=10,
    random_state=42
)

#AQUI YA TENEMOS EL MODELO ENTRENADO
print("\n[Retraso] Entrenando red neuronal... (puede tardar varios minutos)")

#Entrenar
model_delay.fit(X_train_bal2, y_train_bal2)
print(f"    Epocas entrenadas: {model_delay.n_iter_}")
print(f"    Loss final       : {model_delay.loss_:.4f}")

#Evaluar
y_pred_delay = model_delay.predict(X_test_s2)
print(f"\n    Accuracy : {accuracy_score(y_test, y_pred_delay):.4f}")
print(f"    Precision: {precision_score(y_test, y_pred_delay, zero_division=0):.4f}")
print(f"    Recall   : {recall_score(y_test, y_pred_delay, zero_division=0):.4f}")
print(f"    F1-Score : {f1_score(y_test, y_pred_delay, zero_division=0):.4f}")
print()
print(classification_report(y_test, y_pred_delay,
      target_names=['A tiempo', 'Retraso >=15min'], zero_division=0))
cm2 = confusion_matrix(y_test, y_pred_delay)
print(f"    Matriz de confusion:")
print(f"    [[VN={cm2[0,0]:,}  FP={cm2[0,1]:,}]")
print(f"     [FN={cm2[1,0]:,}  VP={cm2[1,1]:,}]]")

#Guardar modelo y scaler
joblib.dump(model_delay,  'models/modelo_mlp_delay.pkl')
joblib.dump(scaler_delay, 'models/scaler_mlp_delay.pkl')
print('\nModelo retraso guardado correctamente')
print('\n Entrenamiento MLP completado.')

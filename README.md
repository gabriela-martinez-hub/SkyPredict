# ✈️ SkyPredict — Sistema Web de Predicción de Vuelos
### Proyecto: Sistema Web de Predicción con Modelos de Aprendizaje Supervisado

---

## 1. Fuente

| Campo | Detalle |
|---|---|
| **Plataforma** | [Kaggle](https://www.kaggle.com/) |
| **Dataset** | [US National Flight Data 2015 - 2020](https://www.kaggle.com/datasets/bingecode/us-national-flight-data-2015-2020) |
| **Organismo original** | Bureau of Transportation Statistics (BTS), U.S. Department of Transportation |
| **Período cubierto** | 2015 – 2020 |
| **Dominio** | Aviación civil / Transporte aéreo en Estados Unidos |

### ¿Por qué este dataset?

1. **Tamaño y representatividad:** Con más de 36 millones de registros de vuelos reales, ofrece suficiente variedad estadística para entrenar modelos robustos.
2. **Variables ricas:** Contiene información temporal, geográfica y operacional que permite construir modelos predictivos con múltiples características relevantes.
3. **Relevancia práctica:** La predicción de cancelaciones y retrasos tiene alto valor real para pasajeros, aerolíneas y aeropuertos.
4. **Problema de clasificación claro:** Las variables objetivo (`CANCELLED` y retraso ≥ 15 min) son binarias y están bien definidas.
5. **Calidad de datos:** Los valores nulos se concentran en columnas derivadas esperables en vuelos cancelados, lo que facilita el preprocesamiento.

---

## 2. Número de Instancias y Dimensiones

| Métrica | Valor |
|---|---|
| **Instancias (filas)** | 36.063.838 |
| **Variables (columnas)** | 17 |
| **Aerolíneas únicas** | 19 |
| **Período** | 2015 – 2020 |

---

## 3. Descripción de Variables

###  Variables Temporales

| Variable | Tipo | Descripción |
|---|---|---|
| `YEAR` | int | Año del vuelo (2015–2020) |
| `MONTH` | int | Mes del vuelo (1=Enero … 12=Diciembre) |
| `DAY_OF_MONTH` | int | Día del mes (1–31) |
| `DAY_OF_WEEK` | int | Día de la semana (1=Lunes … 7=Domingo) |

### Variables Operacionales

| Variable | Tipo | Descripción |
|---|---|---|
| `OP_UNIQUE_CARRIER` | str | Código IATA de la aerolínea (ej. AA, DL, UA) |
| `CRS_DEP_TIME` | str | Hora de salida programada (HH:MM:SS) |
| `CRS_ARR_TIME` | str | Hora de llegada programada (HH:MM:SS) |
| `AIR_TIME` | float | Tiempo en el aire en minutos |
| `DISTANCE` | int | Distancia del vuelo en millas |

### Variables Geográficas

| Variable | Tipo | Descripción |
|---|---|---|
| `ORIGIN_CITY_NAME` | str | Ciudad de origen |
| `ORIGIN_STATE_ABR` | str | Estado de origen (abreviatura) |
| `DEST_CITY_NAME` | str | Ciudad de destino |
| `DEST_STATE_ABR` | str | Estado de destino (abreviatura) |

### Variables de Rendimiento y Objetivo

| Variable | Tipo | Descripción |
|---|---|---|
| `DEP_DELAY_NEW` | float | Minutos de retraso en salida (0 si puntual) |
| `ARR_DELAY_NEW` | float | Minutos de retraso en llegada (0 si puntual) |
| `CANCELLED` | int | **[TARGET 1]** 1 = vuelo cancelado, 0 = no cancelado |
| `CANCELLATION_CODE` | str | Causa de cancelación: A=Aerolínea, B=Clima, C=Sistema nacional, D=Seguridad |

---

## 4. Variables Objetivo (Targets)

Este proyecto aborda **dos tareas de clasificación binaria**:

### Target 1 — `CANCELLED`
- **Definición:** Indica si un vuelo fue cancelado.
- **Valores:** `0` = No cancelado | `1` = Cancelado
- **Distribución:** ~97.9% no cancelados / ~2.1% cancelados
- **Tipo de problema:** Clasificación binaria

### Target 2 — `DELAYED_15` *(variable derivada)*
- **Definición:** Indica si un vuelo llegó con **15 o más minutos de retraso**.
- **Construcción:** `DELAYED_15 = 1 si ARR_DELAY_NEW >= 15, sino 0`
- **Valores:** `0` = Sin retraso significativo | `1` = Retraso ≥ 15 min
- **Aplica a:** Solo vuelos **no cancelados**.
- **Tipo de problema:** Clasificación binaria

---

## 5. Calidad del Dataset

| Variable | Nulos | % del total | Observación |
|---|---|---|---|
| `YEAR` | 0 | 0.00% | Completa |
| `MONTH` | 0 | 0.00% | Completa |
| `DAY_OF_MONTH` | 0 | 0.00% | Completa |
| `DAY_OF_WEEK` | 0 | 0.00% | Completa |
| `OP_UNIQUE_CARRIER` | 0 | 0.00% | Completa |
| `ORIGIN_CITY_NAME` | 0 | 0.00% | Completa |
| `ORIGIN_STATE_ABR` | 0 | 0.00% | Completa |
| `DEST_CITY_NAME` | 0 | 0.00% | Completa |
| `DEST_STATE_ABR` | 0 | 0.00% | Completa |
| `DISTANCE` | 0 | 0.00% | Completa |
| `CANCELLED` | 0 | 0.00% | Completa |
| `CRS_DEP_TIME` | 5.782 | 0.02% | Mínimo, imputable |
| `CRS_ARR_TIME` | 102.116 | 0.28% | Bajo, imputable |
| `DEP_DELAY_NEW` | 753.457 | 2.09% | Vuelos cancelados (esperado) |
| `ARR_DELAY_NEW` | 855.002 | 2.37% | Vuelos cancelados (esperado) |
| `AIR_TIME` | 852.404 | 2.36% | Vuelos cancelados (esperado) |
| `CANCELLATION_CODE` | 35.296.707 | 97.87% |  Normal: solo aplica a vuelos cancelados (~2.1%) |

> **Nota:** Los nulos en `DEP_DELAY_NEW`, `ARR_DELAY_NEW`, `AIR_TIME` y `CANCELLATION_CODE` son **estructurales y esperados**: un vuelo cancelado no tiene tiempos de vuelo ni retrasos registrables.

## 6. Preprocesamiento y Selección de Variables

Para la preparación del dataset se definió un flujo de procesamiento estructurado, el cual permite limpiar, transformar y seleccionar las variables más relevantes para el entrenamiento del modelo.

### Flujo de procesamiento aplicado

1. **Carga de datos**
   - Se cargó el archivo `flights_top3.csv`, previamente filtrado para las aerolíneas principales (WN, DL, AA).

2. **Creación de variable objetivo derivada**
   - Se construyó la variable `DELAYED_15` a partir de `ARR_DELAY_NEW`:
   - `DELAYED_15 = 1` si `ARR_DELAY_NEW ≥ 15`, en caso contrario `0`.

3. **Eliminación de variables innecesarias**
   - Se eliminaron las siguientes columnas:
     - `ARR_DELAY_NEW`
     - `DEP_DELAY_NEW`
     - `AIR_TIME`
     - `CANCELLATION_CODE`
     - `DISTANCE`

   - **Justificación:**
     - `ARR_DELAY_NEW` se elimina porque fue utilizada para construir la variable objetivo `DELAYED_15`.
     - `DEP_DELAY_NEW` se elimina para evitar fuga de información (*data leakage*), ya que está altamente correlacionada con los retrasos.
     - `AIR_TIME` y `DISTANCE` no aportan valor significativo en este enfoque del modelo.
     - `CANCELLATION_CODE` presenta una alta proporción de valores nulos y no es útil para la predicción.

4. **Imputación de valores nulos**
   - Se imputaron los valores faltantes en:
     - `CRS_DEP_TIME`
     - `CRS_ARR_TIME`
   - Se utilizó la **mediana**, debido a su robustez ante valores atípicos.

5. **Transformación de variables temporales**
   - `CRS_DEP_TIME` y `CRS_ARR_TIME` fueron convertidas a valores numéricos (minutos) para facilitar su uso en modelos de machine learning.

6. **Eliminación de registros con datos faltantes**
   - Se eliminaron las filas con valores nulos en variables críticas del modelo.

7. **Codificación de variables categóricas**
   - Se aplicó **Label Encoding** a las variables categóricas (`OP_UNIQUE_CARRIER`, `ORIGIN_STATE_ABR`, `DEST_STATE_ABR`, `ORIGIN_CITY_NAME`, `DEST_CITY_NAME`).
   - Los encoders resultantes se guardaron en `models/label_encoders.pkl` para que el backend (`app.py`) pueda codificar correctamente las entradas del usuario con los mismos valores usados en el entrenamiento.

8. **Exportación del dataset procesado**
   - El dataset final fue guardado como `flights_processed.csv`.

---

###  Variables finales utilizadas

Después del proceso de limpieza y selección, el modelo trabaja únicamente con las siguientes variables de entrada:

- `YEAR`
- `MONTH`
- `DAY_OF_MONTH`
- `DAY_OF_WEEK`
- `OP_UNIQUE_CARRIER`
- `ORIGIN_CITY_NAME`
- `ORIGIN_STATE_ABR`
- `DEST_CITY_NAME`
- `DEST_STATE_ABR`
- `CRS_DEP_TIME`
- `CRS_ARR_TIME`

---

###  Variables eliminadas

Las variables eliminadas del modelo fueron:

- `ARR_DELAY_NEW`
- `DEP_DELAY_NEW`
- `AIR_TIME`
- `CANCELLATION_CODE`
- `DISTANCE`

---

###  Variables objetivo del modelo

El sistema trabaja con **dos variables de salida (targets)**:

- `DELAYED_15`: Indica si el vuelo presenta un retraso mayor o igual a 15 minutos.
- `CANCELLED`: Indica si el vuelo fue cancelado.

> La variable `CANCELLED` no se utiliza como variable de entrada, sino como una **variable objetivo adicional**, al igual que `DELAYED_15`.

Esto permite abordar el problema desde dos enfoques:

- Predicción de retrasos significativos (clasificación binaria)
- Predicción de cancelaciones (clasificación binaria)

---

## 7. Instrucciones de Ejecución

### Requisitos previos

- Python 3.10 o superior instalado
- El archivo `flights_top3.csv` ubicado en la carpeta raíz del proyecto
- Terminal con PowerShell (Windows) o bash (Mac/Linux)

---

### Paso 1 — Crear el entorno virtual

El entorno virtual aísla las dependencias del proyecto para que no interfieran con otras instalaciones de Python en el equipo.

**Windows (PowerShell):**
```powershell
python -m venv env
```

**Mac / Linux:**
```bash
python3 -m venv env
```

---

### Paso 2 — Activar el entorno virtual

Debe activarse cada vez que se abra una nueva terminal antes de correr cualquier script.

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env\Scripts\Activate.ps1
```

Al activarse correctamente, el prompt de la terminal mostrará `(env)` al inicio.

**Mac / Linux:**
```bash
source env/bin/activate
```

---

### Paso 3 — Instalar dependencias

Con el entorno virtual activado, instalar todas las librerías del proyecto:

```bash
pip install -r requirements.txt
```

Las dependencias principales son:

| Librería | Uso |
|---|---|
| `Flask` | Backend — servidor web y API |
| `flask-cors` | Permite la conexión entre frontend y backend |
| `pandas` | Manejo y transformación del dataset |
| `scikit-learn` | Modelos de ML (KNN, MLP) y preprocesamiento |
| `joblib` | Guardar y cargar los modelos entrenados (.pkl) |
| `numpy` | Operaciones numéricas |

---

### Paso 4 — Preprocesar el dataset

Genera `flights_processed.csv` y `models/label_encoders.pkl` a partir de `flights_top3.csv`:

```bash
python preprocessing.py
```

Este paso puede tardar varios minutos dependiendo del hardware. Al finalizar correctamente imprime:
```
Preprocesamiento completado.
```

> **Si el proceso tarda demasiado:** agregar `df = df.sample(n=1_000_000, random_state=42)` justo después del `pd.read_csv` en `preprocessing.py`. Con 1 millón de filas el resultado es representativo y el proceso tarda 1-2 minutos.

---

### Paso 5 — Entrenar los modelos

Entrenar el modelo KNN:
```bash
python train_KNN.py
```

Entrenar la Red Neuronal (MLP):
```bash
python train_RED_NEURONAL.py
```

Cada script genera sus archivos `.pkl` en la carpeta `models/` e imprime las métricas de evaluación en consola. Al finalizar cada uno debe aparecer:
```
Entrenamiento KNN completado.
Entrenamiento MLP completado.
```

La carpeta `models/` debe quedar con los siguientes archivos:
```
models/
├── label_encoders.pkl
├── encoders_info.pkl
├── modelo_knn_cancel.pkl
├── scaler_knn_cancel.pkl
├── modelo_knn_delay.pkl
├── scaler_knn_delay.pkl
├── modelo_mlp_cancel.pkl
├── scaler_mlp_cancel.pkl
├── modelo_mlp_delay.pkl
└── scaler_mlp_delay.pkl
```

---

### Paso 6 — Iniciar el servidor

```bash
python app.py
```

La consola debe mostrar:
```
Modelos KNN cargados correctamente
Modelos MLP cargados correctamente
http://localhost:5000
```

---

### Paso 7 — Abrir la aplicación

Abrir el navegador y navegar a:
```
http://localhost:5000
```

Para verificar que el backend y los modelos están activos:
```
http://localhost:5000/api/status
```

Respuesta esperada:
```json
{
  "servidor": "ok",
  "modelo_cancel": true,
  "modelo_delay": true,
  "modelos_listos": true
}
```

---

### Resumen del orden de ejecución

```
1. Activar entorno virtual
2. pip install -r requirements.txt   (solo la primera vez)
3. python preprocessing.py           (genera flights_processed.csv y label_encoders.pkl)
4. python train_KNN.py               (genera modelos KNN)
5. python train_RED_NEURONAL.py      (genera modelos MLP)
6. python app.py                     (inicia el servidor)
7. Abrir http://localhost:5000
```

---

## 8. Modelos de Machine Learning

### 8.1 Modelo KNN (K-Nearest Neighbors)

Archivo: `train_KNN.py`

KNN es el algoritmo más intuitivo de aprendizaje supervisado. Para predecir si un vuelo nuevo se cancela, busca los K vuelos más similares en el dataset de entrenamiento y vota por mayoría. No aprende parámetros durante el entrenamiento — memoriza los datos y compara en el momento de predecir.

**Parámetros:**

| Parámetro | Valor | Justificación |
|---|---|---|
| `n_neighbors` | 7 | K más alto reduce sobreajuste respecto a K=1 o K=3 |
| `weights` | `distance` | Vecinos más cercanos pesan más — mejora con desbalanceo |
| `metric` | `minkowski` (p=2) | Equivale a distancia euclidiana estándar |

**Escalado:** se usa `StandardScaler` porque KNN mide distancias. Sin escalar, variables con rangos grandes (`CRS_DEP_TIME`: 0–1439 min) dominarían sobre variables pequeñas (`MONTH`: 1–12), haciendo que la distancia no tenga sentido real.

**Manejo del desbalanceo:** se aplicó undersampling sobre el conjunto de entrenamiento:
- Cancelación: ratio 5:1 (5 no cancelados por cada cancelado)
- Retraso: ratio 3:1 (3 a tiempo por cada retrasado)

El conjunto de prueba (test) no se modificó para que las métricas reflejen la distribución real.

**Resultados:**

| Predicción | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| Cancelación | 0.9380 | 0.18 | 0.65 | 0.28 |
| Retraso ≥15min | 0.7804 | 0.32 | 0.29 | 0.30 |

---

### 8.2 Red Neuronal (MLP — Multilayer Perceptron)

Archivo: `train_RED_NEURONAL.py`

El MLP es una red neuronal artificial compuesta por capas de neuronas interconectadas. Aprende ajustando los pesos de las conexiones en cada iteración para minimizar el error de predicción. A diferencia del KNN, sí tiene un proceso de entrenamiento explícito.

**Arquitectura y parámetros:**

| Parámetro | Valor | Justificación |
|---|---|---|
| `hidden_layer_sizes` | `(64, 32)` | Dos capas ocultas: 64 neuronas → 32 neuronas → salida |
| `activation` | `relu` | Función estándar: devuelve max(0, x), eficiente y estable |
| `solver` | `adam` | Optimizador adaptativo, robusto para datasets grandes |
| `alpha` | `0.001` | Regularización L2 para penalizar pesos excesivos |
| `learning_rate_init` | `0.001` | Velocidad de aprendizaje inicial |
| `max_iter` | `500` | Máximo de épocas de entrenamiento |
| `early_stopping` | `True` | Detiene el entrenamiento si el error no mejora en 10 épocas consecutivas |

**Resultados:**

| Predicción | Accuracy | Precision | Recall | F1-Score | Épocas |
|---|---|---|---|---|---|
| Cancelación | 0.9700 | 0.32 | 0.52 | 0.39 | 72 |
| Retraso ≥15min | 0.8333 | 0.44 | 0.04 | 0.07 | 44 |

---

### 8.3 Selección del modelo final

| Predicción | Modelo seleccionado | F1-Score | Razón |
|---|---|---|---|
| Cancelación | **Red Neuronal (MLP)** | 0.39 | Mejor F1 y mayor Precision (menos falsas alarmas) |
| Retraso ≥15min | **KNN** | 0.30 | El MLP no converge para esta tarea (F1 = 0.07) |

Para el análisis completo de métricas, interpretación de resultados y justificación detallada de la selección, ver el documento [`METRICAS_MODELOS.md`](METRICAS_MODELOS.md).

---

## 9. Estructura del Proyecto

```
SkyPredict/
├── env/                          
├── models/                       # Modelos entrenados (.pkl)
│   ├── label_encoders.pkl        # LabelEncoders de variables categóricas
│   ├── encoders_info.pkl         # Info de rangos por columna
│   ├── modelo_knn_cancel.pkl
│   ├── scaler_knn_cancel.pkl
│   ├── modelo_knn_delay.pkl
│   ├── scaler_knn_delay.pkl
│   ├── modelo_mlp_cancel.pkl
│   ├── scaler_mlp_cancel.pkl
│   ├── modelo_mlp_delay.pkl
│   └── scaler_mlp_delay.pkl
├── app.py                        # Backend Flask — API de predicción
├── preprocessing.py              # Limpieza y transformación del dataset
├── train_KNN.py                  # Entrenamiento modelo KNN
├── train_RED_NEURONAL.py         # Entrenamiento Red Neuronal (MLP)
├── index.html                    # Frontend — interfaz de usuario
├── style.css                     # Estilos del frontend
├── frontend.js                   # Lógica del frontend
├── estados_ciudades.csv          # Referencia de estados y ciudades
├── notebooks.ipynb               # Análisis exploratorio de datos
├── flights_top3.csv              # Dataset original filtrado
├── flights_processed.csv         # Dataset procesado
├── requirements.txt              # Dependencias del proyecto
├── METRICAS_MODELOS.md           # Análisis de métricas y selección de modelo
└── README.md                     # Este archivo
```

### .gitignore recomendado

```
env/
flights_top3.csv
flights_processed.csv
models/
__pycache__/
*.pyc
```

---

*Proyecto SkyPredict — Ciencia de los Datos — 2026*

#  Descripción del Dataset
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

### 🔄 Flujo de procesamiento aplicado

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
   - Se aplicó **Label Encoding** a las variables categóricas.

8. **Exportación del dataset procesado**
   - El dataset final fue guardado como `flights_processed.csv`.

---

###  Variables finales utilizadas

Después del proceso de limpieza y selección, el modelo trabaja únicamente con las siguientes variables:

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
- `CANCELLED`

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

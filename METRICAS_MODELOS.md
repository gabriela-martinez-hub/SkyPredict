# 📊 Evaluación de Modelos — SkyPredict

---

## 1. ¿Qué métricas se utilizaron y qué significa cada una?

Antes de analizar los resultados, es importante entender qué mide cada métrica y por qué se eligieron estas en particular.

En ambos modelos el problema es de **clasificación binaria**: el modelo debe decidir entre dos respuestas posibles (por ejemplo, "Cancelado" o "No cancelado"). Para evaluar qué tan bien lo hace, se usaron cuatro métricas:

---

### Accuracy (Exactitud)

Mide el porcentaje de predicciones correctas sobre el total.

```
Accuracy = (predicciones correctas) / (total de predicciones)
```

**¿Por qué no es suficiente sola?**
En este proyecto el dataset está desbalanceado: el 98.1% de los vuelos no se cancela. Si un modelo dijera siempre "No cancelado" sin aprender nada, tendría 98.1% de accuracy. Por eso esta métrica sola es engañosa y se necesitan las siguientes tres.

---

### Precision (Precisión)

De todos los vuelos que el modelo predijo como cancelados (o retrasados), ¿cuántos realmente lo eran?

```
Precision = Verdaderos Positivos / (Verdaderos Positivos + Falsos Positivos)
```

Un valor bajo de precision significa que el modelo genera muchas **falsas alarmas**: le dice al pasajero que su vuelo se cancelará cuando en realidad no es así.

---

### Recall (Sensibilidad)

De todos los vuelos que realmente se cancelaron (o retrasaron), ¿cuántos logró detectar el modelo?

```
Recall = Verdaderos Positivos / (Verdaderos Positivos + Falsos Negativos)
```

Un valor bajo de recall significa que el modelo **se pierde muchos casos reales**: vuelos que sí se cancelaron pero el modelo dijo que no.

**En este proyecto el Recall es la métrica más importante.** Es peor que un modelo no detecte una cancelación real (el pasajero llega al aeropuerto para nada) que generar una falsa alarma (el pasajero se preocupa innecesariamente).

---

### F1-Score

Es el balance entre Precision y Recall. Penaliza cuando uno de los dos es muy bajo.

```
F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
```

Es la **métrica principal de comparación** entre modelos cuando hay desbalanceo de clases, porque resume en un solo número qué tan bien el modelo detecta la clase minoritaria sin generar demasiadas falsas alarmas.

---

### Matriz de Confusión

Muestra en detalle cómo se distribuyeron los errores y aciertos:

|  | Predijo: NO | Predijo: SÍ |
|---|---|---|
| **Real: NO** | Verdadero Negativo (VN) | Falso Positivo (FP) |
| **Real: SÍ** | Falso Negativo (FN) | Verdadero Positivo (VP) |

- **VN:** El vuelo no se canceló y el modelo dijo que no → correcto
- **FP:** El vuelo no se canceló pero el modelo dijo que sí → falsa alarma
- **FN:** El vuelo sí se canceló pero el modelo dijo que no → el más costoso
- **VP:** El vuelo sí se canceló y el modelo lo detectó → correcto

---

## 2. Resultados del Modelo KNN

### Predicción de Cancelación

| Métrica | Clase: No cancelado | Clase: Cancelado |
|---|---|---|
| Precision | 0.99 | **0.18** |
| Recall | 0.94 | **0.65** |
| F1-Score | 0.97 | **0.28** |
| **Accuracy global** | | **0.9380** |

**Matriz de confusión:**
```
                 Predijo: No cancelado   Predijo: Cancelado
Real: No cancel.      3,264,645              195,051
Real: Cancelado          23,483               43,038
```

**Interpretación:**

El KNN logró detectar el **65% de las cancelaciones reales** (Recall = 0.65), lo cual es un resultado positivo dado el desbalanceo extremo del dataset (solo 1.9% de vuelos se cancela). Sin embargo, su Precision es baja (0.18), lo que significa que de cada 100 vuelos que predijo como cancelados, solo 18 realmente lo eran. En números concretos, generó 195,051 falsas alarmas contra 43,038 detecciones correctas.

El F1-Score de 0.28 refleja este desequilibrio: el modelo es útil para detectar cancelaciones (buen Recall) pero genera demasiado ruido (baja Precision).

---

### Predicción de Retraso ≥ 15 min

| Métrica | Clase: A tiempo | Clase: Retraso |
|---|---|---|
| Precision | 0.86 | **0.32** |
| Recall | 0.88 | **0.29** |
| F1-Score | 0.87 | **0.30** |
| **Accuracy global** | | **0.7804** |

**Matriz de confusión:**
```
               Predijo: A tiempo   Predijo: Retraso
Real: A tiempo    2,533,611           356,103
Real: Retraso       403,730           166,253
```

**Interpretación:**

Para retrasos el KNN tiene un desempeño más equilibrado entre Precision (0.32) y Recall (0.29), aunque ambos son bajos. El modelo solo detectó el **29% de los retrasos reales** — es decir, dejó pasar 403,730 retrasos sin detectarlos. El F1-Score de 0.30 indica que el modelo tiene dificultades para distinguir entre vuelos a tiempo y vuelos retrasados, posiblemente porque los patrones de retraso son más sutiles y dependientes de factores externos (clima, tráfico aéreo) que no están en las variables disponibles.

---

## 3. Resultados del Modelo Red Neuronal (MLP)

### Predicción de Cancelación

| Métrica | Clase: No cancelado | Clase: Cancelado |
|---|---|---|
| Precision | 0.99 | **0.32** |
| Recall | 0.98 | **0.52** |
| F1-Score | 0.98 | **0.39** |
| **Accuracy global** | | **0.9700** |
| **Épocas entrenadas** | | **72 de 500** |
| **Loss final** | | **0.2697** |

**Matriz de confusión:**
```
                 Predijo: No cancelado   Predijo: Cancelado
Real: No cancel.      3,385,995               73,701
Real: Cancelado          32,192               34,329
```

**Interpretación:**

La Red Neuronal mejora significativamente respecto al KNN en la predicción de cancelaciones. Con un F1-Score de **0.39 vs 0.28**, logra un mejor equilibrio entre detectar cancelaciones reales y no generar falsas alarmas. Su Precision subió de 0.18 a **0.32** (casi el doble), lo que significa que genera menos falsas alarmas por cada cancelación que detecta. El Recall bajó de 0.65 a **0.52**, es decir, detecta menos cancelaciones reales que el KNN, pero las que detecta son más confiables.

El hecho de que el entrenamiento se detuviese en la **época 72 de 500** confirma que el `early_stopping` funcionó correctamente: el modelo dejó de mejorar y se detuvo para evitar sobreentrenamiento.

---

### Predicción de Retraso ≥ 15 min

| Métrica | Clase: A tiempo | Clase: Retraso |
|---|---|---|
| Precision | 0.84 | **0.44** |
| Recall | 0.99 | **0.04** |
| F1-Score | 0.91 | **0.07** |
| **Accuracy global** | | **0.8333** |
| **Épocas entrenadas** | | **44 de 500** |
| **Loss final** | | **0.5340** |

**Matriz de confusión:**
```
               Predijo: A tiempo   Predijo: Retraso
Real: A tiempo    2,860,841            28,873
Real: Retraso       547,721            22,262
```

**Interpretación:**

Este es el resultado más preocupante de todos los modelos. La Red Neuronal para retraso tiene un Recall de apenas **0.04** — solo detectó el 4% de los retrasos reales, dejando pasar 547,721 casos sin detectar. El F1-Score de 0.07 es muy bajo.

¿Qué pasó? El `early_stopping` detuvo el entrenamiento en la **época 44** con un Loss de 0.5340, que es relativamente alto. Esto indica que el modelo no convergió bien — posiblemente la arquitectura (64→32 neuronas) no es suficiente para capturar los patrones de retraso, o el undersampling con ratio 3:1 no fue suficiente para este desbalanceo (83.5% vs 16.5%).

---

## 4. Comparativa entre modelos

### Cancelación de vuelo

| Modelo | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| KNN | 0.9380 | 0.18 | **0.65** | 0.28 |
| **Red Neuronal (MLP)** | **0.9700** | **0.32** | 0.52 | **0.39** |

### Retraso ≥ 15 min

| Modelo | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **KNN** | 0.7804 | 0.32 | **0.29** | **0.30** |
| Red Neuronal (MLP) | 0.8333 | 0.44 | 0.04 | 0.07 |

---

## 5. Selección del modelo final

### Para predicción de Cancelación → **Red Neuronal (MLP)**

Se selecciona la Red Neuronal como modelo principal para cancelación por las siguientes razones:

**1. Mejor F1-Score (0.39 vs 0.28):** el F1 es la métrica de referencia con datos desbalanceados porque penaliza cuando Precision o Recall son extremos. La Red Neuronal logra un mejor equilibrio entre ambos.

**2. Mayor Precision (0.32 vs 0.18):** el KNN genera casi tres veces más falsas alarmas por cada cancelación real que detecta. Desde la perspectiva del usuario, recibir falsas alarmas constantemente haría que dejara de confiar en el sistema.

**3. Menor cantidad de falsas alarmas:** el KNN generó 195,051 falsas alarmas contra 73,701 de la Red Neuronal. Aunque el KNN detecta más cancelaciones reales (43,038 vs 34,329), lo hace a un costo muy alto en falsos positivos.

**4. El early_stopping funcionó:** el modelo se detuvo en la época 72 con un Loss de 0.2697, lo cual indica que aprendió patrones reales sin sobreentrenarse.

El KNN sigue siendo útil como modelo de referencia (baseline) y su alto Recall (0.65) lo hace preferible en contextos donde perder una cancelación real sea el peor escenario posible.

---

### Para predicción de Retraso → **KNN**

Se selecciona el KNN como modelo principal para retraso por una razón directa:

**El MLP prácticamente no detecta retrasos (Recall = 0.04, F1 = 0.07).** Con un F1-Score de 0.30 vs 0.07, el KNN es claramente superior para este problema.

La Red Neuronal para retraso converge en solo 44 épocas con un Loss alto (0.5340), lo que indica que no logró aprender patrones útiles. Esto puede deberse a que el problema de retraso es inherentemente más difícil: los retrasos dependen de factores como el clima, el tráfico aéreo y eventos operacionales que no están capturados en las variables disponibles (fecha, aerolínea, origen, destino, horarios). El KNN al menos detecta el 29% de los retrasos reales.

---

## 6. Conclusión general

| Predicción | Modelo seleccionado | F1-Score | Justificación |
|---|---|---|---|
| Cancelación | Red Neuronal (MLP) | 0.39 | Mejor balance Precision/Recall, menos falsas alarmas |
| Retraso ≥15min | KNN | 0.30 | MLP no converge para esta tarea (F1=0.07) |

Ambos modelos presentan limitaciones esperables dado el desbalanceo del dataset y la naturaleza del problema. Los retrasos y cancelaciones de vuelos dependen en gran medida de factores externos (condiciones climáticas, congestión del espacio aéreo, problemas mecánicos) que no están disponibles como variables de entrada al momento de la predicción. Los modelos trabajaron exclusivamente con información programada previamente: fecha, aerolínea, horarios y ubicación.

---

*Proyecto SkyPredict — Ciencia de los Datos — 2026*

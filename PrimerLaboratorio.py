# -*- coding: utf-8 -*-
"""
Editor de Spyder
Este es un archivo temporal.
"""
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Leer registro
record = wfdb.rdrecord('01')

# Tomar solo un segmento (4000 muestras)
senal = record.p_signal[:4000, 0]
# Eliminar valores NaN
senal = senal[~np.isnan(senal)]

N = len(senal)

#MOSTRAR GRÁFICA DE DATOS TOMADOS
plt.figure(figsize=(12,4))
plt.plot(senal)
plt.title("Señal ECG - Apnea Database")
plt.xlabel("Muestras")
plt.ylabel("Amplitud")
plt.show()


# ---------------------------
#  MÉTODO MANUAL
# ---------------------------

# Media
media_manual = sum(senal) / N

# Desviación estándar
suma = 0
for x in senal:
    suma += (x - media_manual) ** 2
desv_manual = (suma / N) ** 0.5

# Coeficiente de variación
if media_manual != 0:
    cv_manual = desv_manual / media_manual
else:
    cv_manual = 0

# Skewness
suma_skew = 0
for x in senal:
    suma_skew += ((x - media_manual) / desv_manual) ** 3
skew_manual = suma_skew / N

# Curtosis
suma_kurt = 0
for x in senal:
    suma_kurt += ((x - media_manual) / desv_manual) ** 4
kurt_manual = suma_kurt / N

# ---------------------------
#  MÉTODO CON PYTHON
# ---------------------------
# Media
media_np = np.mean(senal)
# Desviación estándar
desv_np = np.std(senal)
#Coeficiente de variación
cv_np = desv_np / media_np
# Skewness
skew_np = stats.skew(senal)
# Curtosis
kurt_np = stats.kurtosis(senal, fisher=False)  # para que coincida con el manual

# ---------------------------
#  RESULTADOS
# ---------------------------

print("===== RESULTADOS MANUALES =====")
print("Media:", media_manual)
print("Desv estándar:", desv_manual)
print("CV:", cv_manual)
print("Skewness:", skew_manual)
print("Curtosis:", kurt_manual)

print("\n===== RESULTADOS PYTHON =====")
print("Media:", media_np)
print("Desv estándar:", desv_np)
print("CV:", cv_np)
print("Skewness:", skew_np)
print("Curtosis:", kurt_np)


# Gráfica de histograma
plt.figure(figsize=(8,5))
plt.hist(senal, bins=50, density=True)
plt.title("Histograma normalizado")
plt.xlabel("Amplitud")
plt.ylabel("Densidad")
plt.grid(True)
plt.show()



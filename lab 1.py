# -*- coding: utf-8 -*-
"""
Editor de Spyder
Este es un archivo temporal.
"""
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

#SNR
def calcular_snr(signal, noisy_signal):
    ruido = noisy_signal - signal
    pot_senal = np.mean(signal**2)
    pot_ruido = np.mean(ruido**2)
    snr = 10 * np.log10(pot_senal / pot_ruido)
    return snr

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
plt.figure(figsize=(6,4))
plt.hist(senal, bins=50, density=True)
plt.title("Histograma normalizado")
plt.xlabel("Amplitud")
plt.ylabel("Densidad")
plt.grid(True)
plt.show()


#Ruido Gaussiano
ruido_gauss = np.random.normal(0, 0.05, len(senal))
senal_gauss = senal + ruido_gauss

snr_gauss = calcular_snr(senal, senal_gauss)
print("SNR Ruido Gaussiano:", snr_gauss)

plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
plt.plot(senal)
plt.title("Señal Original")
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(senal_gauss)
plt.title("Señal con Ruido Gaussiano")
plt.grid(True)

plt.tight_layout()
plt.show()

#Ruido impulso
senal_impulso = senal.copy()

cantidad_impulsos = int(0.02 * len(senal))  # 2% de muestras
indices = np.random.randint(0, len(senal), cantidad_impulsos)

senal_impulso[indices] = np.max(senal) * 3

snr_impulso = calcular_snr(senal, senal_impulso)
print("SNR Ruido Impulso:", snr_impulso)

plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
plt.plot(senal)
plt.title("Señal Original")
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(senal_impulso)
plt.title("Señal con Ruido Impulso")
plt.grid(True)

plt.tight_layout()
plt.show()


#Ruido tipo artefacto
t = np.linspace(0, 10, len(senal))
artefacto = 0.2 * np.sin(2*np.pi*0.5*t)

senal_artefacto = senal + artefacto

snr_artefacto = calcular_snr(senal, senal_artefacto)
print("SNR Artefacto:", snr_artefacto)

plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
plt.plot(senal)
plt.title("Señal Original")
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(senal_artefacto)
plt.title("Señal con Ruido tipo Artefacto")
plt.grid(True)

plt.tight_layout()
plt.show()


#Comparativa

plt.figure(figsize=(15,8))

plt.subplot(4,1,1)
plt.plot(senal)
plt.title("Señal Original")

plt.subplot(4,1,2)
plt.plot(senal_gauss)
plt.title("Ruido Gaussiano")

plt.subplot(4,1,3)
plt.plot(senal_impulso)
plt.title("Ruido Impulso")

plt.subplot(4,1,4)
plt.plot(senal_artefacto)
plt.title("Ruido Artefacto")

plt.tight_layout()
plt.show()
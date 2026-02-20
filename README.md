# Análisis estadístico de señales 
## Primer Laboratorio procesamiento digital de señales

**Maria Camila Ospina Jara, Juan Felipe Serna Alarcón**

### Descripción
En este laboratorio se realizó la caracterización estadística de una señal biomédica con el fin de describir su comportamiento mediante parámetros descriptivos. 
Se trabajó con características no fiduciales, es decir, aquellas que analizan la señal como un conjunto completo sin depender de la detección de puntos específicos 
como picos o eventos particulares.
El objetivo principal fue calcular y analizar parámetros estadísticos como la media, desviación estándar, coeficiente de variación, asimetría, curtosis e 
histogramas, utilizando herramientas de programación en Python. Estos cálculos se realizaron tanto implementando las fórmulas desde cero como empleando funciones 
predefinidas de librerías especializadas.

### Desarrollo de la páctica 
### Parte A: Señal de Physionet
En esta primera etapa del laboratorio se descargó una señal ECG desde PhysioNet (Brno University of Technology ECG Database) y se realizó su importación, visualización y análisis estadístico.

**Señal ECG importada**

![Señal ECG physionet](ECGdata.png)


Se calcularon los siguientes parámetros:
+ Media
+ Desviación estándar
+ Coeficiente de variación
+ Skewness
+ Curtosis

Manualmente (programando las fórmulas)
```python
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

}
```
Usando funciones de NumPy y SciPy
```python
# Media
media_np = np.mean(senal)
# Desviación estándar
desv_np = np.std(senal)
#Coeficiente de variación
cv_np = desv_np / media_np #el coeficiente siempre es positivo
# Skewness
skew_np = stats.skew(senal)
# Curtosis
kurt_np = stats.kurtosis(senal, fisher=False)  # para que coincida con el manual

```
Y se obtuvieron los siquientes resultados

Media: -0.19348138119299282

Desv estándar: 0.2946382102175074

CV: 1.5228246170292385

Skewness: 1.3747776389974853

Curtosis: 11.601684982096616

***Histograma***

Con el fin de analizar la distribución estadística de la señal ECG, se construyó un histograma de sus valores de amplitud.
El histograma permite visualizar la frecuencia con la que aparecen determinados rangos de amplitud dentro de la señal, proporcionando una representación gráfica de su comportamiento estadístico.
Esta herramienta es útil para evaluar la simetría, dispersión y forma de la distribución, lo cual se relaciona directamente con parámetros como la media, la desviación estándar, la asimetría (skewness) y la curtosis.

![Histograma](HistogramaA.png)

---

### Parte B: Captura de la señal
Se generó una señal ECG usando un generador fisiológico y fue adquirida mediante STM32


Muestra de los primero 5 segundos de la señal
<img width="860" height="400" alt="image" src="https://github.com/user-attachments/assets/57dab01b-6b05-41cd-870a-e860490ea6c2" />

Los estadisticos de esos 5 seg

----- ANALISIS ECG (5 s) -----

Media: 0.0014590164967198459

Desviacion estandar: 0.22663213223260037

Coeficiente de variacion: 155.33212457988904

Asimetria (skewness): 1.6704965004522951

Curtosis: 6.3865478790626895

--Histograma de la señal--

<img width="545" height="367" alt="image" src="https://github.com/user-attachments/assets/efa80824-f349-48eb-96c8-7b80489dd78a" />


### Parte C: 
Se contaminó la señal con:
+ Ruido Gaussiano

<img width="637" height="190" alt="image" src="https://github.com/user-attachments/assets/0b691369-d239-446f-aebf-53845ad94a42" />

```python
def ruido_gaussiano(signal, sigma=0.05):
    ruido = np.random.normal(0, sigma, len(signal))
    return signal + ruido# posteriormente se llamo la funcion para aplicar el ruido lo mismo para los demas tipos de ruido
```
 
+ Ruido Impulso

<img width="645" height="192" alt="image" src="https://github.com/user-attachments/assets/26429956-7544-4b76-823b-edb9adbf514e" />


```python
def ruido_impulso(signal, prob=0.01, amp=2):
    signal_ruido = signal.copy()
    n = len(signal)

    for i in range(n):
        if np.random.rand() < prob:
            signal_ruido[i] += amp * (2*np.random.rand()-1)

    return signal_ruido
```
+ Ruido tipo Artefacto

<img width="617" height="182" alt="image" src="https://github.com/user-attachments/assets/634bbb92-a3da-4ba4-a837-c94d583183aa" />


```python
def ruido_artefacto(signal, fs):
    t = np.arange(len(signal))/fs
    
    # movimiento base respiratorio
    baseline = 0.3*np.sin(2*np.pi*0.3*t)
    
    # ruido muscular EMG
    emg = 0.15*np.sin(2*np.pi*35*t) * np.random.randn(len(signal))

    return signal + baseline + emg
```
***Señales con ruido***

![Señales contaminadas con ruido](Señalconruido.png)

Se calculó la Relación Señal-Ruido (SNR) usando:

SNR = 10 log10(Pseñal / Pruido)

Se obtuvo: 
SNR Ruido Gaussiano: 16.99 dB

SNR Ruido Impulso: -5.40 dB

SNR Artefacto: 7.93 dB

### Análisis
+ El ruido gaussiano produjo una SNR de 16.99 dB, indicando una calidad de señal moderadamente afectada. Aunque la señal aún conserva su estructura principal, la dispersión aumenta debido a la naturaleza aleatoria del ruido.
+ El ruido impulso generó una SNR negativa (-5.40 dB), lo que indica que la potencia del ruido supera la de la señal original. Este tipo de ruido introduce valores extremos que distorsionan significativamente la señal biomédica, afectando su análisis estadístico y posible interpretación clínica.
+ El ruido tipo artefacto produjo una SNR de 7.93 dB, indicando una degradación considerable de la señal. Este tipo de ruido afecta principalmente la línea base, generando desplazamientos que pueden alterar parámetros estadísticos como la media.

## Referencias

[1] L. Maršánová, A. Nemcova, R. Smisek, L. Smital, & M. Vitek (2021).  
Brno University of Technology ECG Signal Database with Annotations of P Wave (BUT PDB).  
PhysioNet. https://doi.org/10.13026/hvvj-5b53

[2] A. L. Goldberger et al. (2000).  
PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals.  
Circulation, 101(23), e215–e220.

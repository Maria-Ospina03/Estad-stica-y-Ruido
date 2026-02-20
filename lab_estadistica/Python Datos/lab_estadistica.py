#llamado de librerias de PYQT6

import sys
from PyQt6 import uic,QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import *
from PyQt6.QtGui import *

#Llamado de librerias para uso del puerto serial

import serial.tools.list_ports
import serial
import numpy as np
import struct

#importar libreria para creacion de hilos

import threading

#Importar la libreria para graficar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#librerias para llamar el archivo
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import re


#------------librerias para el tratamiento de señales-
from scipy.signal import butter, filtfilt
from scipy.stats import skew, kurtosis

#Importar libreria para grabar datos

import tkinter as tk
import time
import threading
import random
#------------------------------------------------------------------------
def filtrar_ecg(signal, fs):
    # Filtro pasa banda 0.5 - 40 Hz (estándar clínico)
    low = 0.5/(fs/2)
    high = 40/(fs/2)
    b,a = butter(3,[low,high],btype='band')
    return filtfilt(b,a,signal)

#-----CONTAMIB
def ruido_gaussiano(signal, sigma=0.05):
    ruido = np.random.normal(0, sigma, len(signal))
    return signal + ruido

def ruido_impulso(signal, prob=0.01, amp=2):
    signal_ruido = signal.copy()
    n = len(signal)

    for i in range(n):
        if np.random.rand() < prob:
            signal_ruido[i] += amp * (2*np.random.rand()-1)

    return signal_ruido

def ruido_artefacto(signal, fs):
    t = np.arange(len(signal))/fs
    
    # movimiento base respiratorio
    baseline = 0.3*np.sin(2*np.pi*0.3*t)
    
    # ruido muscular EMG
    emg = 0.15*np.sin(2*np.pi*35*t) * np.random.randn(len(signal))

    return signal + baseline + emg

#calcular snr
def calcular_snr(senal_limpia, senal_ruidosa):

    senal_limpia = np.array(senal_limpia)
    senal_ruidosa = np.array(senal_ruidosa)

    ruido = senal_ruidosa - senal_limpia

    potencia_senal = np.sum(senal_limpia**2)
    potencia_ruido = np.sum(ruido**2)

    snr = 10 * np.log10(potencia_senal / potencia_ruido)

    return snr

#---------------------------------------------------------------------
def escalar_adc(valor):
        # 0 → -1.5
        # 4095 → +1.5
        return (valor / 4095.0) * 3.0 - 1.5 

#Variables globales para grabacion

grabando = False

fila=1
datosserial=[12,11,10,9,8,7,6,5,4,3,2,1,13,14,15,16,17,18,19,20,21,22,23,24,25]

#Creacion de la clase principal 
    
class principal(QMainWindow):
    
    def __init__(self):

        # Poner la direccion del desinger para abrir la ventana
        
        super(principal,self).__init__()
        uic.loadUi("Ventana.ui",self)
        # Variables para el conteo de BPM
        self.umbral_bpm = 2500           # ajustable según la señal
        self.ultimo_pico = None
        self.bpm = 0
#Llamar la funcion de verificacion de los puertos de comunicacion

        self.puertosdisponibles()
        self.ser = None

#Llamar la funcion conectar / Grabar cada vez que se da click sobre el boton

        self.ConectW.clicked.connect(self.conectarCOM)
        self.GrabarW.clicked.connect(self.grabar_datos)
#cargar los datos
        self.CargarW.clicked.connect(self.cargar_datos)

#Hacer la grafica
        self.x = np.linspace(0,10,1000)
        self.y = np.linspace(0,0,1000)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.graficawidget.setLayout(layout)


    
    def actualizar_grafica_archivo(self):
        if self.indice_actual < len(self.datos_np):
            # Agregar el siguiente punto
            self.x_data.append(self.indice_actual)
            self.y_data.append(self.datos_np[self.indice_actual, 0])
            self.linea.set_data(self.x_data, self.y_data)

            # Ajustar límites del eje X
            self.ax.set_xlim(0, max(100, self.indice_actual))
            self.ax.set_ylim(np.min(self.datos_np[:, 0]) - 100, np.max(self.datos_np[:, 0]) + 100)

            # Actualizar gráfica
            self.canvas.draw()
            self.indice_actual += 1
        else:
            # Detener el temporizador cuando termina
            self.timer_replay.stop()


# Funcion para visualizacion de los puertos COM en uso         
        
    def puertosdisponibles(self):
        p= serial.tools.list_ports.comports()
        for port in p:
            #print(port)

            #visualizar los puertos disponibles en el combo que se llama PuertosW
            self.PuertosW.addItem(port.device)

        #print(self.PuertosW)
        #print(port)


#Funcion para conectar al puerto de comunicacion con el boton
            
    def conectarCOM(self):

        #verificar el estado del boton que creamos en la interfaz ConectW
        
        estado= self.ConectW.text()
        self.stop_event_ser= threading.Event()
        
        if estado =="Conectar":
            com= self.PuertosW.currentText()
            try:

                #inicio del puerto serial
                
                self.ser = serial.Serial(com,115200)

                #Inicio del hilo
                
                self.hiloserial = threading.Thread(target=self.periodic_thread)
                self.hiloserial.start()


                print("Puero Serial Conectado")
                self.ConectW.setText("Desconectar")
                
            except serial.SerialException as e:
                print("Error en el puerto de comunicacion serial, ", e)
        else:
            # Cerrar el hilo serial

            self.ser.close()
            self.stop_event_ser.set()
            self.hiloserial.join()

            #Poner desconectado al boton
            
            print("Puero Serial Desconectado")
            self.ConectW.setText("Conectar")


#Funcion para grabar datos al darle click al boton Grabar

    def grabar_datos(self):
        import datetime
        from PyQt6.QtWidgets import QInputDialog

        global grabando, nombre_archivo

        estadoR = self.GrabarW.text()

        if estadoR == "Grabar":
            texto, ok = QInputDialog.getText(self, "Nombre del archivo",
                                         "Escribe un nombre para la grabación:")
            if not ok or texto.strip() == "":
                return

            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = f"{texto}_{fecha_hora}.txt"

            self.archivo_txt = open(nombre_archivo, "w")
            grabando = True

            self.GrabarW.setText("Detener")
            print("Grabando en TXT:", nombre_archivo)

            self.grabaDatos = threading.Thread(target=self.periodic_threadR)
            self.grabaDatos.start()

        else:
            grabando = False
            self.grabaDatos.join()
            self.archivo_txt.close()

            self.GrabarW.setText("Grabar")
            print("Archivo guardado")


#funcion para cargar los datos guardados en grabar

    def cargar_datos(self):
        try:
            ruta_archivo, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar archivo", "", "Archivos TXT (*.txt)"
            )
            if not ruta_archivo:
                return

            datos = []

        # ---- Leer archivo ----
            with open(ruta_archivo, "r") as f:
                for linea in f:
                    valores = linea.strip().split(",")
                    for v in valores:
                        if v != "":
                            datos.append(float(v))

            self.datos_np = np.array(datos)
            
            fs=100

            # ====== GUARDAR SEÑAL ORIGINAL para snr ======
            senal_original = self.datos_np.copy()

            #---Se escribe como codigo dependiendo cual se quiera usar----
            #self.datos_np = ruido_gaussiano(self.datos_np, sigma=0.09)
            #self.datos_np = ruido_impulso(self.datos_np, prob=0.05, amp=2.5)
            self.datos_np = ruido_artefacto(self.datos_np, fs)


            #======guardar la señal del ruido=====
            senal_ruidosa = self.datos_np.copy()

            # ====== CALCULAR SNR ======
            snr_ruido = calcular_snr(senal_original, senal_ruidosa)
            print("\nSNR con el ruido :", snr_ruido, "dB")
            print("Archivo cargado:", ruta_archivo)
            print("Total muestras:", len(self.datos_np))

      #filtrado digital

            fs = 100  # Hz (tu frecuencia de muestreo ~10ms)

        # 1) Filtrar ECG
            self.datos_np = filtrar_ecg(self.datos_np, fs)

        # 2) Quitar offset DC
            self.datos_np = self.datos_np - np.mean(self.datos_np)

        # 3) Normalizar amplitud
            self.datos_np = self.datos_np / np.max(np.abs(self.datos_np))

        # 4) Crear eje de tiempo real
            t = np.arange(len(self.datos_np)) / fs

        # 5) Mostrar solo 5 segundos (estándar monitor cardíaco)
            ventana_seg = 5
            muestras = int(fs * ventana_seg)

            self.ax.clear()
            self.ax.plot(t[:muestras], self.datos_np[:muestras], linewidth=1)
            segmento = self.datos_np[:muestras]
            self.ax.set_title("ECG cargado (5 segundos)")
            self.ax.set_xlabel("Tiempo (s)")
            self.ax.set_ylabel("Amplitud normalizada")
            self.ax.grid(True)

            self.canvas.draw()

            fig2 = Figure()
            ax2 = fig2.add_subplot(111)
            canvas2 = FigureCanvas(fig2)

            ax2.hist(segmento, bins=50)
            ax2.set_title("Histograma amplitud ECG")
            ax2.set_xlabel("Amplitud")
            ax2.set_ylabel("Frecuencia")

            canvas2.show()
            
        except Exception as e:
            print("Error al cargar:", e)

        # ------------------- ANALISIS ESTADISTICO -------------------
        

        media = np.mean(segmento)
        desv = np.std(segmento)
        coef_var = desv / media if media != 0 else 0
        asimetria = skew(segmento)
        curt = kurtosis(segmento)

        print("----- ANALISIS ECG (5 s) -----")
        print("Media:", media)
        print("Desviacion estandar:", desv)
        print("Coeficiente de variacion:", coef_var)
        print("Asimetria (skewness):", asimetria)
        print("Curtosis:", curt)
        
        #self.mostrar_histograma()
#funcion para crear el hilo

    def periodic_thread(self):
        global datosserial
        if self.ser is not None and self.ser.is_open:
            data=self.ser.read(50)
            data = struct.unpack('50B',data)
            
            for i in range(0,len(data),2):
                    self.y = np.roll(self.y,-1)
                    adc = data[i]*100+data[i+1]
                    self.y[-1] = escalar_adc(adc)

            for i in range(0,25,1):
                datosserial[i] = 100*data[i*2]+data[i*2+1]    
            self.ax.clear()
            self.ax.plot(self.x, self.y)
            self.ax.grid(True)
            self.canvas.draw()
            print(self.y)
        if not self.stop_event_ser.is_set():
            #print("Hilo en ejecucion")                
            threading.Timer(1e-2,self.periodic_thread).start()
        self.detectar_bpm()


#Hilo Para Grabar datos

    def periodic_threadR(self):
        global datosserial

        if grabando:
            threading.Timer(1e-2, self.periodic_threadR).start()

            linea = []

            for i in range(25):
                valor = escalar_adc(datosserial[i])
                linea.append(f"{valor:.5f}")

            self.archivo_txt.write(",".join(linea) + "\n")

#funcion para el conteo de BPM       
    def detectar_bpm(self):
        # Últimas 3 muestras para detectar un pico real
        y0 = self.y[-3]
        y1 = self.y[-2]
        y2 = self.y[-1]

        # --- Umbral dinámico ---
        # Auto-ajusta según la señal real
        umbral = np.mean(self.y) + 0.35 * np.std(self.y)

        # Confirmar pico local tipo R-peak
        es_pico = (y1 > umbral) and (y1 > y0) and (y1 > y2)

        if not es_pico:
            return

        tiempo_actual = time.time()

        # Si ya hubo un pico previo → calcular intervalo
        if self.ultimo_pico is not None:
            intervalo = tiempo_actual - self.ultimo_pico

              # Bloqueo de ruido: 250 ms mínimo entre picos
            if intervalo < 0.25:
                return
    
            bpm_instantaneo = 60 / intervalo

        # Validación fisiológica (descartar picos raros)
            if 40 < bpm_instantaneo < 180:
            # Suavizado exponencial (da estabilidad)
                self.bpm = int(self.bpm * 0.6 + bpm_instantaneo * 0.4)
                self.BPMlabel.setText(f"BPM: {self.bpm}")

    # Registrar pico
        self.ultimo_pico = tiempo_actual

# Main Program, para hacer llamado a la funcion principal

if __name__=="__main__":
    app= QApplication(sys.argv)
    ventana = principal()
    ventana.show()
    sys.exit(app.exec())

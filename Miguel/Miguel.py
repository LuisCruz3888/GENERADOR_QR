#importar las librerias
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import csv
import serial
import serial.tools.list_ports
import threading
import time
import numpy as np
from collections import deque

class BaseVentana(tk.Tk):
    #definir el construcctor
    def __init__(self, titulo="Ventana Base", tamano="400x300"):
        super().__init__()
        self.title(titulo)
        self.geometry(tamano)
        self.configuracion_grid()
    
    # configurar el grid
    def configuracion_grid(self, filas=4,columnas=2):
        """configura la distribución de la ventana usando grid y colores de fondo"""
        for i in range(filas):
            self.rowconfigure(i,weight=1, minsize=50) #definir filas
        for j in range(columnas):
            self.columnconfigure(j,weight=1, minsize=100) #definir columnas
        # Nota: antes se dibujaban labels de fondo para visualizar la grilla.
        # Se elimina esa lógica para no interferir con los widgets reales.
    #configurar un boton 
    def definir_boton(self, texto, comando, fila=0, columna=0, rowspan=1, colspan=1, parent=None, sticky="nsew"):
        """Crear un boton y posicionarlo en el contenedor usando grid"""
        if parent is None:
            parent = self
        boton = ttk.Button(parent, text=texto, command=comando)
        boton.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        return boton
    def definir_input(self, ancho=20, fila=1, columna=0, rowspan=1, colspan=1, parent=None, sticky="nsew"):
        """Crear una entrada de texto y posicionarla en grid"""
        if parent is None:
            parent = self
        input_var = tk.StringVar()
        entrada = ttk.Entry(parent, textvariable=input_var, width=ancho)
        entrada.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        return entrada, input_var
    def definir_texarea(self, ancho=40, alto=10, fila=2, columna=0, rowspan=1, colspan=1, parent=None, sticky="nsew"):
        """Crear un área de texto con scrollbar y posicionarla en grid"""
        if parent is None:
            parent = self
        textarea = tk.Text(parent, width=ancho, height=alto)
        textarea.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        # Scrollbar vertical
        try:
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=textarea.yview)
            textarea.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=fila, column=columna+colspan, rowspan=rowspan, sticky="ns", padx=(0,6), pady=6)
        except Exception:
            pass
        return textarea 
    def actualizar_textarea(self,textarea, texto):
        """inserta texto en el area de texto y lo desplaza automaticamente"""
        textarea.insert(tk.END,texto+"\n")  
        textarea.see(tk.END)
    def definir_menu_desplegable(self, opciones, fila=3, columna=0, rowspan=1, colspan=1, parent=None, sticky="nsew"):
        """Crear un menú desplegable y posicionarlo con grid"""
        if parent is None:
            parent = self
        opcion_var = tk.StringVar()
        opcion_var.set(opciones[0] if opciones else "")
        menu = ttk.Combobox(parent, textvariable=opcion_var, values=opciones, state="readonly")
        menu.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        return menu, opcion_var
    def definir_canvas(self, figura, fila=4, columna=1, rowspan=1, colspan=1, parent=None, sticky="nsew"):
        if parent is None:
            parent = self
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        # Permitir expansión dentro del frame
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        canvas = FigureCanvasTkAgg(figura, master=canvas_frame)
        widget = canvas.get_tk_widget()
        widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        return canvas
    def definir_label(self, texto, fila=4, columna=1, rowspan=1, colspan=1, parent=None, sticky="w"):
        if parent is None:
            parent = self
        label = ttk.Label(parent, text=texto)
        label.grid(row=fila, column=columna, rowspan=rowspan, columnspan=colspan, padx=6, pady=6, sticky=sticky)
        return label
        
#Clase para manejar los datos del MPU6050
class SensorMPU6050:
    def __init__(self, max_puntos=100):
        self.max_puntos = max_puntos
        self.tiempo = deque(maxlen=max_puntos)
        self.accel_x = deque(maxlen=max_puntos)
        self.accel_y = deque(maxlen=max_puntos)
        self.accel_z = deque(maxlen=max_puntos)
        self.gyro_x = deque(maxlen=max_puntos)
        self.gyro_y = deque(maxlen=max_puntos)
        self.gyro_z = deque(maxlen=max_puntos)
        self.tiempo_inicio = time.time()
        
    def agregar_datos(self, ax, ay, az, gx, gy, gz):
        tiempo_actual = time.time() - self.tiempo_inicio
        self.tiempo.append(tiempo_actual)
        self.accel_x.append(ax)
        self.accel_y.append(ay)
        self.accel_z.append(az)
        self.gyro_x.append(gx)
        self.gyro_y.append(gy)
        self.gyro_z.append(gz)

class Figura:
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Configurar subplot para acelerómetro
        self.ax1.set_title("Acelerómetro (m/s²)")
        self.ax1.set_xlabel("Tiempo (s)")
        self.ax1.set_ylabel("Aceleración")
        self.ax1.legend(["X", "Y", "Z"])
        self.ax1.grid(True)
        
        # Configurar subplot para giroscopio
        self.ax2.set_title("Giroscopio (°/s)")
        self.ax2.set_xlabel("Tiempo (s)")
        self.ax2.set_ylabel("Velocidad Angular")
        self.ax2.legend(["X", "Y", "Z"])
        self.ax2.grid(True)
        
    def actualizar_grafico(self, sensor_data):
        if len(sensor_data.tiempo) < 2:
            return
            
        # Limpiar ejes
        self.ax1.clear()
        self.ax2.clear()
        
        # Graficar datos del acelerómetro
        self.ax1.plot(sensor_data.tiempo, sensor_data.accel_x, 'r-', label='X', linewidth=2)
        self.ax1.plot(sensor_data.tiempo, sensor_data.accel_y, 'g-', label='Y', linewidth=2)
        self.ax1.plot(sensor_data.tiempo, sensor_data.accel_z, 'b-', label='Z', linewidth=2)
        self.ax1.set_title("Acelerómetro (m/s²)")
        self.ax1.set_xlabel("Tiempo (s)")
        self.ax1.set_ylabel("Aceleración")
        self.ax1.legend()
        self.ax1.grid(True)
        
        # Graficar datos del giroscopio
        self.ax2.plot(sensor_data.tiempo, sensor_data.gyro_x, 'r-', label='X', linewidth=2)
        self.ax2.plot(sensor_data.tiempo, sensor_data.gyro_y, 'g-', label='Y', linewidth=2)
        self.ax2.plot(sensor_data.tiempo, sensor_data.gyro_z, 'b-', label='Z', linewidth=2)
        self.ax2.set_title("Giroscopio (°/s)")
        self.ax2.set_xlabel("Tiempo (s)")
        self.ax2.set_ylabel("Velocidad Angular")
        self.ax2.legend()
        self.ax2.grid(True)
        
        # Ajustar layout
        self.fig.tight_layout(pad=3.0)
        
    def obtener_figura(self):
        return self.fig

class APP(BaseVentana):
    def __init__(self):
        super().__init__("Monitor MPU6050 - Arduino", tamano="1200x800")
        # La ventana principal usará una grilla 1x1 para que el PanedWindow ocupe todo
        self.configuracion_grid(filas=1, columnas=1)   
        
        # Variables para comunicación serial
        self.serial_connection = None
        self.conectado = False
        self.hilo_lectura = None
        self.sensor_data = SensorMPU6050()
        self.arduino_detectado = None
        # Parámetros de adquisición
        self.sample_time_ms = 50  # tiempo de muestreo deseado (ms)
        self.samples_target = 0   # 0 = infinito o libre
        self.adquiriendo = False
        self.samples_count = 0
        
        # Obtener puertos disponibles
        self.puertos_disponibles = self.obtener_puertos()
        self.baudrates = ["9600", "57600", "115200"]
        
        # PanedWindow principal (horizontal): izquierda (controles) | derecha (gráfico)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky="nsew")

        # Panel izquierdo con dos secciones apiladas
        left = ttk.Frame(paned)
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Panel derecho para el gráfico
        right = ttk.Frame(paned)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        # Guardamos referencia para recrear canvas al cerrar gráfica estática
        self.panel_derecho = right

        paned.add(left, weight=1)
        paned.add(right, weight=3)

        # Grupo: Conexión
        grp_conn = ttk.Labelframe(left, text="Conexión")
        grp_conn.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        for i in range(6):
            grp_conn.columnconfigure(i, weight=1)
        grp_conn.rowconfigure(2, weight=1)

        self.boton_conectar = self.definir_boton("Conectar", self.toggle_conexion, fila=0, columna=0, parent=grp_conn)
        self.boton_refrescar = self.definir_boton("🔄 Buscar", self.refrescar_puertos, fila=0, columna=1, parent=grp_conn)
        self.boton_auto_conectar = self.definir_boton("🔌 Auto", self.auto_conectar, fila=0, columna=2, parent=grp_conn)
        # Botón de diagnóstico eliminado para simplificar la interfaz en la entrega
        self.boton_cerrar = self.definir_boton("🔌 Cerrar", self.desconectar_arduino, fila=0, columna=3, parent=grp_conn)

        self.definir_label("Puerto", fila=1, columna=0, parent=grp_conn)
        self.menu_puertos, self.puerto_seleccionado = self.definir_menu_desplegable(self.puertos_disponibles, fila=1, columna=1, colspan=2, parent=grp_conn, sticky="ew")
        self.definir_label("Baudios", fila=1, columna=3, parent=grp_conn)
        self.menu_baud, self.baud_var = self.definir_menu_desplegable(self.baudrates, fila=1, columna=4, parent=grp_conn, sticky="ew")
        self.baud_var.set("9600")
        self.label_estado = self.definir_label("🔴 Desconectado", fila=2, columna=0, colspan=5, parent=grp_conn, sticky="w")
        self.textarea = self.definir_texarea(fila=3, columna=0, colspan=6, parent=grp_conn, sticky="nsew")

        # Grupo: Adquisición y datos
        grp_acq = ttk.Labelframe(left, text="Adquisición y Datos")
        grp_acq.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        for i in range(8):
            grp_acq.columnconfigure(i, weight=1)

        self.definir_label("Tiempo (ms)", fila=0, columna=0, parent=grp_acq)
        self.entry_ts, self.ts_var = self.definir_input(ancho=10, fila=0, columna=1, parent=grp_acq)
        self.ts_var.set(str(self.sample_time_ms))
        self.definir_label("# Muestras", fila=0, columna=2, parent=grp_acq)
        self.entry_n, self.n_var = self.definir_input(ancho=10, fila=0, columna=3, parent=grp_acq)
        self.n_var.set("0")
        self.boton_adq = self.definir_boton("▶ Iniciar", self.iniciar_adquisicion, fila=0, columna=4, parent=grp_acq)
        self.boton_detener_adq = self.definir_boton("⏹ Detener", self.detener_adquisicion, fila=0, columna=5, parent=grp_acq)

        self.definir_label("Nombre datos", fila=1, columna=0, parent=grp_acq)
        self.entry_nombre, self.nombre_var = self.definir_input(ancho=20, fila=1, columna=1, colspan=2, parent=grp_acq)
        self.nombre_var.set("datos_mpu6050")
        self.boton_guardar = self.definir_boton("💾 Guardar CSV", self.guardar_csv, fila=1, columna=3, parent=grp_acq)

        self.signales = [
            ("AccelX", "accel_x"), ("AccelY", "accel_y"), ("AccelZ", "accel_z"),
            ("GyroX", "gyro_x"), ("GyroY", "gyro_y"), ("GyroZ", "gyro_z")
        ]
        self.tipos_graf = ["Serie temporal", "Histograma", "FFT", "Boxplot"]
        self.definir_label("Señal", fila=2, columna=0, parent=grp_acq)
        self.menu_senal, self.senal_var = self.definir_menu_desplegable([s[0] for s in self.signales], fila=2, columna=1, parent=grp_acq, sticky="ew")
        self.senal_var.set("AccelX")
        self.definir_label("Tipo", fila=2, columna=2, parent=grp_acq)
        self.menu_tipo, self.tipo_var = self.definir_menu_desplegable(self.tipos_graf, fila=2, columna=3, parent=grp_acq, sticky="ew")
        self.tipo_var.set("Serie temporal")
        self.boton_graficar = self.definir_boton("📈 Generar gráfica", self.generar_grafica, fila=2, columna=4, colspan=2, parent=grp_acq)
        # Botones para gestionar la gráfica generada
        self.boton_guardar_graf = self.definir_boton("🖼 Guardar gráfica", self.guardar_grafica, fila=2, columna=6, parent=grp_acq)
        self.boton_cerrar_graf = self.definir_boton("🔙 Cerrar gráfica", self.cerrar_grafica, fila=2, columna=7, parent=grp_acq)

        # Panel derecho: gráfico
        self.figura_obj = Figura()
        self.canvas = self.definir_canvas(self.figura_obj.obtener_figura(), fila=0, columna=0, parent=self.panel_derecho, sticky="nsew")
        # Modo: False = lectura en vivo; True = vista estática de gráfica generada
        self.vista_estatica = False
        
        # Configurar actualización de gráfico
        self._after_id = self.after(100, self.actualizar_interfaz)

        # Manejar cierre de ventana limpiamente
        self.protocol("WM_DELETE_WINDOW", self.destruir)
        
        # Mensaje inicial y conexión automática
        self.actualizar_textarea(self.textarea, "🚀 Monitor MPU6050 iniciado")
        self.actualizar_textarea(self.textarea, f"📡 Puertos encontrados: {len(self.puertos_disponibles)}")
        
        if self.arduino_detectado:
            self.actualizar_textarea(self.textarea, f"🎯 Arduino detectado en: {self.arduino_detectado}")
            self.actualizar_textarea(self.textarea, "🔄 Intentando conexión automática en 2 segundos...")
            self.after(2000, self.auto_conectar)  # Conectar automáticamente después de 2 segundos
        else:
            self.actualizar_textarea(self.textarea, "⚠️ Arduino no detectado automáticamente")
            self.actualizar_textarea(self.textarea, "💡 Presiona '🔌 Auto-Conectar' o selecciona puerto manualmente")
    
    def obtener_puertos(self):
        """Obtiene una lista de puertos COM disponibles"""
        puertos = []
        arduino_encontrado = None
        
        for puerto in serial.tools.list_ports.comports():
            # Verificar si es un Arduino por descripción o VID/PID
            es_arduino = False
            descripcion = puerto.description.lower()
            
            # Detectar Arduino por descripción común
            if any(keyword in descripcion for keyword in ['arduino', 'ch340', 'cp210', 'ftdi']):
                es_arduino = True
            
            # Detectar Arduino por VID/PID (Vendor ID/Product ID)
            if puerto.vid and puerto.pid:
                # VIDs comunes de Arduino
                arduino_vids = [0x2341, 0x1A86, 0x0403, 0x10C4]  # Arduino, CH340, FTDI, CP210x
                if puerto.vid in arduino_vids:
                    es_arduino = True
            
            # Verificar si el puerto está disponible
            try:
                test_serial = serial.Serial(puerto.device, 9600, timeout=0.1)
                test_serial.close()
                
                if es_arduino:
                    arduino_encontrado = puerto.device
                    puertos.insert(0, f"{puerto.device} (Arduino detectado)")
                else:
                    puertos.append(puerto.device)
            except:
                # Puerto ocupado o no disponible
                if es_arduino:
                    puertos.insert(0, f"{puerto.device} (Arduino ocupado)")
                else:
                    puertos.append(f"{puerto.device} (ocupado)")
        
        # Si encontramos un Arduino disponible, lo guardamos
        self.arduino_detectado = arduino_encontrado
        
        return puertos if puertos else ["No hay puertos disponibles"]
    
    def refrescar_puertos(self):
        """Refresca la lista de puertos disponibles"""
        self.actualizar_textarea(self.textarea, "🔄 Buscando Arduino...")
        self.puertos_disponibles = self.obtener_puertos()
        self.menu_puertos['values'] = self.puertos_disponibles
        if self.puertos_disponibles:
            self.puerto_seleccionado.set(self.puertos_disponibles[0])
        
        if self.arduino_detectado:
            self.actualizar_textarea(self.textarea, f"✅ Arduino encontrado en: {self.arduino_detectado}")
        else:
            self.actualizar_textarea(self.textarea, "❌ Arduino no detectado automáticamente")
        
        self.actualizar_textarea(self.textarea, f"📡 Puertos disponibles: {', '.join([p.split(' (')[0] for p in self.puertos_disponibles])}")
    
    def auto_conectar(self):
        """Conecta automáticamente al Arduino detectado"""
        if self.conectado:
            self.actualizar_textarea(self.textarea, "⚠️ Ya estás conectado")
            return
            
        if self.arduino_detectado:
            # Establecer el puerto del Arduino en el menú
            for puerto in self.puertos_disponibles:
                if self.arduino_detectado in puerto:
                    self.puerto_seleccionado.set(puerto)
                    break
            
            self.actualizar_textarea(self.textarea, f"🔌 Conectando automáticamente a {self.arduino_detectado}...")
            self.conectar_arduino()
        else:
            self.actualizar_textarea(self.textarea, "❌ No se detectó Arduino automáticamente")
            self.actualizar_textarea(self.textarea, "🔄 Presiona 'Buscar Arduino' para reescanear")
            self.actualizar_textarea(self.textarea, "📋 O selecciona un puerto manualmente del menú")
    
    def diagnosticar_arduino(self):
        """Realiza un diagnóstico completo del Arduino"""
        self.actualizar_textarea(self.textarea, "🔧 INICIANDO DIAGNÓSTICO...")
        self.actualizar_textarea(self.textarea, "=" * 50)
        
        # 1. Verificar puertos disponibles
        self.actualizar_textarea(self.textarea, "1️⃣ Verificando puertos COM...")
        puertos_raw = []
        for puerto in serial.tools.list_ports.comports():
            puertos_raw.append(f"{puerto.device} - {puerto.description}")
        
        if puertos_raw:
            self.actualizar_textarea(self.textarea, f"✅ Puertos encontrados: {len(puertos_raw)}")
            for puerto in puertos_raw:
                self.actualizar_textarea(self.textarea, f"   📡 {puerto}")
        else:
            self.actualizar_textarea(self.textarea, "❌ No se encontraron puertos COM")
            return
        
        # 2. Probar conexión a cada puerto
        self.actualizar_textarea(self.textarea, "\n2️⃣ Probando conexión a cada puerto...")
        
        for puerto_info in serial.tools.list_ports.comports():
            puerto = puerto_info.device
            self.actualizar_textarea(self.textarea, f"🔍 Probando {puerto}...")
            
            try:
                # Probar conexión
                test_serial = serial.Serial(puerto, 9600, timeout=2)
                time.sleep(2)
                
                # Leer datos por 3 segundos
                datos_encontrados = []
                for i in range(6):  # 6 intentos de 0.5 segundos
                    if test_serial.in_waiting > 0:
                        try:
                            linea = test_serial.readline().decode('utf-8', errors='ignore').strip()
                            if linea:
                                datos_encontrados.append(linea)
                        except:
                            pass
                    time.sleep(0.5)
                
                test_serial.close()
                
                if datos_encontrados:
                    self.actualizar_textarea(self.textarea, f"✅ {puerto}: RESPONDE")
                    self.actualizar_textarea(self.textarea, f"   📊 Datos recibidos: {len(datos_encontrados)} líneas")
                    for i, dato in enumerate(datos_encontrados[:3]):  # Mostrar solo las primeras 3 líneas
                        self.actualizar_textarea(self.textarea, f"   📝 Línea {i+1}: {dato}")
                    
                    # Verificar formato MPU6050
                    datos_texto = " ".join(datos_encontrados)
                    if "AX:" in datos_texto and "GX:" in datos_texto:
                        self.actualizar_textarea(self.textarea, f"🎯 {puerto}: FORMATO MPU6050 CORRECTO")
                    else:
                        self.actualizar_textarea(self.textarea, f"⚠️ {puerto}: Datos no son formato MPU6050")
                else:
                    self.actualizar_textarea(self.textarea, f"❌ {puerto}: No envía datos")
                    
            except Exception as e:
                if "PermissionError" in str(e) or "Access" in str(e):
                    self.actualizar_textarea(self.textarea, f"🔒 {puerto}: OCUPADO por otro programa")
                else:
                    self.actualizar_textarea(self.textarea, f"❌ {puerto}: Error - {str(e)}")
        
        self.actualizar_textarea(self.textarea, "\n🔧 DIAGNÓSTICO COMPLETO")
        self.actualizar_textarea(self.textarea, "=" * 50)
        self.actualizar_textarea(self.textarea, "💡 Si no ves datos MPU6050, verifica:")
        self.actualizar_textarea(self.textarea, "   1. Código arduino_mpu6050.ino está cargado")
        self.actualizar_textarea(self.textarea, "   2. Sensor MPU6050 está conectado correctamente")
        self.actualizar_textarea(self.textarea, "   3. Arduino IDE está cerrado")
    
    def toggle_conexion(self):
        """Alterna entre conectar y desconectar"""
        if not self.conectado:
            self.conectar_arduino()
        else:
            self.desconectar_arduino()
    
    def conectar_arduino(self):
        """Establece conexión con Arduino"""
        try:
            puerto = self.puerto_seleccionado.get()
            if puerto == "No hay puertos disponibles":
                self.actualizar_textarea(self.textarea, "❌ Error: No hay puertos disponibles")
                return
            
            # Limpiar el nombre del puerto de descripciones adicionales
            puerto_limpio = puerto.split(" (")[0]  # Remover "(Arduino detectado)", "(ocupado)", etc.
            
            # Cerrar conexión previa si existe
            if self.serial_connection:
                self.serial_connection.close()
                time.sleep(1)
            
            # Usar el baudrate seleccionado
            try:
                baud_sel = int(self.baud_var.get()) if hasattr(self, 'baud_var') else 9600
            except:
                baud_sel = 9600
            self.actualizar_textarea(self.textarea, f"🔌 Conectando a {puerto_limpio} @ {baud_sel} bps...")
            
            try:
                self.serial_connection = serial.Serial(
                    port=puerto_limpio,
                    baudrate=baud_sel,
                    timeout=2,
                    write_timeout=2,
                    exclusive=True
                )
                time.sleep(2)
                self.serial_connection.reset_input_buffer()
            except Exception as e:
                raise e
            
            # Intentar leer una línea para validar
            datos_recibidos = ""
            for _ in range(5):
                if self.serial_connection.in_waiting > 0:
                    try:
                        linea = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if linea:
                            datos_recibidos = linea
                            self.actualizar_textarea(self.textarea, f"📡 Datos recibidos: {linea}")
                            break
                    except:
                        pass
                time.sleep(1)
            
            # Conectar aunque no lleguen datos aún (algunos sketches tardan)
            self.conectado = True
            self.boton_conectar.config(text="🔴 Desconectar")
            self.label_estado.config(text=f"🟢 Conectado: {puerto_limpio} ({baud_sel} bps)")
            self.hilo_lectura = threading.Thread(target=self.leer_datos_serial, daemon=True)
            self.hilo_lectura.start()
            self.actualizar_textarea(self.textarea, f"✅ ¡CONECTADO! {puerto_limpio} a {baud_sel} bps")
            if not datos_recibidos:
                self.actualizar_textarea(self.textarea, "⌛ Esperando datos del Arduino...")
            
        except serial.SerialException as se:
            error_msg = str(se)
            if "PermissionError" in error_msg or "Access" in error_msg:
                self.actualizar_textarea(self.textarea, f"❌ Puerto {puerto_limpio} ocupado")
                self.mostrar_solucion_puerto_ocupado()
            else:
                self.actualizar_textarea(self.textarea, f"❌ Error serial: {error_msg}")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error: {str(e)}")
            self.actualizar_textarea(self.textarea, "💡 Verifica que el código Arduino esté cargado correctamente")
    
    def mostrar_solucion_puerto_ocupado(self):
        """Muestra soluciones para puerto ocupado"""
        self.actualizar_textarea(self.textarea, "")
        self.actualizar_textarea(self.textarea, "🔧 SOLUCIONES:")
        self.actualizar_textarea(self.textarea, "1. Cierra Arduino IDE")
        self.actualizar_textarea(self.textarea, "2. Cierra Monitor Serial de Arduino")
        self.actualizar_textarea(self.textarea, "3. Desconecta y reconecta el cable USB")
        self.actualizar_textarea(self.textarea, "4. Prueba con otro puerto COM")
        self.actualizar_textarea(self.textarea, "5. Reinicia el programa")
    
    def desconectar_arduino(self):
        """Desconecta de Arduino"""
        try:
            self.conectado = False
            if self.serial_connection:
                self.serial_connection.close()
                self.serial_connection = None
            
            self.boton_conectar.config(text="🔌 Conectar Arduino")
            self.label_estado.config(text="🔴 Desconectado")
            self.actualizar_textarea(self.textarea, "🔌 Desconectado del Arduino")
            self.actualizar_textarea(self.textarea, "💡 Presiona 'Auto-Conectar' para reconectar automáticamente")
            
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error al desconectar: {str(e)}")
    
    def leer_datos_serial(self):
        """Lee datos del puerto serial en un hilo separado"""
        while self.conectado and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    linea = self.serial_connection.readline().decode('utf-8').strip()
                    self.procesar_datos(linea)
            except Exception as e:
                if self.conectado:  # Solo mostrar error si aún estamos conectados
                    self.actualizar_textarea(self.textarea, f"Error leyendo datos: {str(e)}")
                break
    
    def procesar_datos(self, linea):
        """Procesa los datos recibidos del Arduino"""
        try:
            # Formato esperado: "AX:valor,AY:valor,AZ:valor,GX:valor,GY:valor,GZ:valor"
            if "AX:" in linea and "AY:" in linea and "AZ:" in linea:
                # Parsear los datos
                datos = {}
                for parte in linea.split(','):
                    if ':' in parte:
                        clave, valor = parte.split(':')
                        datos[clave] = float(valor)
                
                # Agregar datos al sensor
                if all(key in datos for key in ['AX', 'AY', 'AZ', 'GX', 'GY', 'GZ']):
                    self.sensor_data.agregar_datos(
                        datos['AX'], datos['AY'], datos['AZ'],
                        datos['GX'], datos['GY'], datos['GZ']
                    )
                    
                    # Contador de adquisición
                    if self.adquiriendo:
                        self.samples_count += 1
                        if self.samples_target > 0 and self.samples_count >= self.samples_target:
                            self.adquiriendo = False
                            self.actualizar_textarea(self.textarea, "✅ Adquisición completada")
                    
                    # Mostrar últimos valores en textarea
                    info = f"A: ({datos['AX']:.2f}, {datos['AY']:.2f}, {datos['AZ']:.2f}) | G: ({datos['GX']:.2f}, {datos['GY']:.2f}, {datos['GZ']:.2f})"
                    self.actualizar_textarea(self.textarea, info)
                    
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"Error procesando datos: {str(e)}")
    
    def actualizar_interfaz(self):
        """Actualiza la interfaz gráfica periódicamente"""
        if (not self.vista_estatica) and self.conectado and len(self.sensor_data.tiempo) > 1:
            try:
                self.figura_obj.actualizar_grafico(self.sensor_data)
                self.canvas.draw()
            except Exception as e:
                print(f"Error actualizando gráfico: {e}")
        
        # Programar siguiente actualización
        try:
            self._after_id = self.after(100, self.actualizar_interfaz)
        except tk.TclError:
            # La ventana puede estar cerrándose
            pass

    def destruir(self):
        # Cancelar actualizaciones pendientes y cerrar serial
        try:
            if hasattr(self, '_after_id') and self._after_id:
                self.after_cancel(self._after_id)
        except Exception:
            pass
        try:
            self.desconectar_arduino()
        except Exception:
            pass
        self.destroy()
    
    def encendido(self):
        """Función de prueba para el botón"""
        texto = self.text_var.get() if hasattr(self, 'text_var') else "Test"
        self.actualizar_textarea(self.textarea, f"ingresando: {texto}")

    # ===== Nuevas funciones de adquisición, guardado y visualización =====
    def iniciar_adquisicion(self):
        try:
            # Leer parámetros de entrada
            ts = int(self.ts_var.get()) if self.ts_var.get() else self.sample_time_ms
            n = int(self.n_var.get()) if self.n_var.get() else 0
            if ts <= 0:
                ts = 50
            self.sample_time_ms = ts
            self.samples_target = max(0, n)
            self.samples_count = 0
            self.adquiriendo = True
            # Limpiar datos si se va a capturar un bloque
            if self.samples_target > 0:
                self.sensor_data = SensorMPU6050(max_puntos=max(1000, self.samples_target))
            self.actualizar_textarea(self.textarea, f"▶ Adquisición iniciada: Ts={ts} ms, N={self.samples_target if self.samples_target>0 else '∞'}")
            
            # Enviar configuración al Arduino (opcional; el sketch debe soportarlo)
            try:
                if self.conectado and self.serial_connection:
                    cmd = f"CFG:TS={ts},N={n}\n"
                    self.serial_connection.write(cmd.encode('utf-8'))
                    self.actualizar_textarea(self.textarea, f"➡ Enviado a Arduino: {cmd.strip()}")
            except Exception as e:
                self.actualizar_textarea(self.textarea, f"⚠ No se pudo enviar configuración: {e}")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error iniciando adquisición: {e}")

    def detener_adquisicion(self):
        self.adquiriendo = False
        self.actualizar_textarea(self.textarea, "⏹ Adquisición detenida por el usuario")

    def guardar_csv(self):
        try:
            nombre = self.nombre_var.get().strip() if self.nombre_var.get() else "datos_mpu6050"
            if not nombre.lower().endswith('.csv'):
                nombre += '.csv'
            # Elegir carpeta destino
            carpeta = filedialog.askdirectory(title="Selecciona la carpeta para guardar el CSV")
            if not carpeta:
                self.actualizar_textarea(self.textarea, "⚠ Guardado cancelado por el usuario")
                return
            ruta = os.path.join(carpeta, nombre)
            # Preparar datos
            filas = zip(
                list(self.sensor_data.tiempo),
                list(self.sensor_data.accel_x), list(self.sensor_data.accel_y), list(self.sensor_data.accel_z),
                list(self.sensor_data.gyro_x), list(self.sensor_data.gyro_y), list(self.sensor_data.gyro_z)
            )
            with open(ruta, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["time", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"])
                writer.writerows(filas)
            self.actualizar_textarea(self.textarea, f"💾 Datos guardados en {ruta}")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error guardando CSV: {e}")

    def _get_selected_series(self):
        etiqueta = self.senal_var.get()
        mapping = {k: v for k, v in self.signales}
        attr = mapping.get(etiqueta, 'accel_x')
        serie = np.array(getattr(self.sensor_data, attr)) if len(self.sensor_data.tiempo) > 1 else np.array([])
        t = np.array(self.sensor_data.tiempo) if len(self.sensor_data.tiempo) > 1 else np.array([])
        return t, serie

    def generar_grafica(self):
        try:
            t, y = self._get_selected_series()
            if y.size < 2:
                self.actualizar_textarea(self.textarea, "⚠ No hay suficientes datos para graficar")
                return
            tipo = self.tipo_var.get()
            # Limpiar figura actual y generar gráfico según tipo
            fig = self.figura_obj.fig
            fig.clear()
            ax = fig.add_subplot(111)
            
            if tipo == "Serie temporal":
                ax.plot(t, y, '-b', linewidth=1.5)
                ax.set_xlabel('Tiempo (s)')
                ax.set_ylabel(self.senal_var.get())
                ax.set_title(f"Serie temporal - {self.senal_var.get()}")
                ax.grid(True)
            elif tipo == "Histograma":
                ax.hist(y, bins=30, color='skyblue', edgecolor='k')
                ax.set_xlabel(self.senal_var.get())
                ax.set_ylabel('Frecuencia')
                ax.set_title(f"Histograma - {self.senal_var.get()}")
                ax.grid(True)
            elif tipo == "FFT":
                # Determinar dt
                if t.size > 1:
                    dt_est = float(np.median(np.diff(t)))
                else:
                    dt_est = max(0.001, self.sample_time_ms/1000.0)
                y_detrend = y - np.mean(y)
                n = len(y_detrend)
                yf = np.fft.rfft(y_detrend)
                xf = np.fft.rfftfreq(n, dt_est)
                ax.plot(xf, np.abs(yf), '-r')
                ax.set_xlabel('Frecuencia (Hz)')
                ax.set_ylabel('Magnitud')
                ax.set_title(f"FFT - {self.senal_var.get()}")
                ax.grid(True)
            elif tipo == "Boxplot":
                ax.boxplot(y, vert=True, patch_artist=True, boxprops=dict(facecolor='lightgreen'))
                ax.set_ylabel(self.senal_var.get())
                ax.set_title(f"Boxplot - {self.senal_var.get()}")
                ax.grid(True)
            else:
                self.actualizar_textarea(self.textarea, f"⚠ Tipo desconocido: {tipo}")
                return
            # Entramos en modo vista estática para no sobreescribir con la actualización en vivo
            self.vista_estatica = True
            self.canvas.draw()
            self.actualizar_textarea(self.textarea, f"📈 Gráfica generada: {tipo} - {self.senal_var.get()}")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error generando gráfica: {e}")

    def guardar_grafica(self):
        try:
            fig = self.figura_obj.fig
            ts = time.strftime("%Y%m%d_%H%M%S")
            nombre_sugerido = f"grafica_{self.tipo_var.get().replace(' ','_')}_{self.senal_var.get()}_{ts}.png"
            ruta = filedialog.asksaveasfilename(
                title="Guardar gráfica",
                initialfile=nombre_sugerido,
                defaultextension=".png",
                filetypes=[("PNG","*.png"), ("PDF","*.pdf"), ("SVG","*.svg")]
            )
            if not ruta:
                return
            fig.savefig(ruta, bbox_inches="tight", dpi=150)
            self.actualizar_textarea(self.textarea, f"🖼 Gráfica guardada: {ruta}")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error al guardar la gráfica: {e}")

    def cerrar_grafica(self):
        try:
            # Volver a la vista de lectura en vivo (dos subgráficas)
            self.vista_estatica = False
            # Recrear la figura y el canvas para restablecer el layout por defecto
            self.figura_obj = Figura()
            # Destruir canvas anterior y crear uno nuevo con la figura por defecto
            try:
                self.canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.canvas = self.definir_canvas(self.figura_obj.obtener_figura(), fila=0, columna=0, parent=self.panel_derecho, sticky="nsew")
            self.actualizar_textarea(self.textarea, "🔙 Cerrada la gráfica. Volviendo a lectura en vivo…")
        except Exception as e:
            self.actualizar_textarea(self.textarea, f"❌ Error al cerrar la gráfica: {e}")
            
                

app=APP()
app.mainloop()
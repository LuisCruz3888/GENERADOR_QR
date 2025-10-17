# Monitor de Movimientos MPU6050 con Arduino

Guía rápida para alguien sin experiencia en Python ni Arduino. Sigue los pasos en orden y todo funcionará.

## 1) ¿Qué es esto?
Una aplicación de escritorio que se conecta a un Arduino con un sensor MPU6050 (acelerómetro y giroscopio) y grafica los datos en tiempo real.

## 2) Qué necesitas
- Un PC con Windows 10/11
- Un Arduino (UNO, Nano o similar)
- Un sensor MPU6050
- Un cable USB para el Arduino

## 3) Conexiones del sensor
MPU6050 → Arduino
- VCC → 5V (o 3.3V)
- GND → GND
- SCL → A5
- SDA → A4

## 4) Preparar el Arduino (una sola vez)
1. Instala el Arduino IDE desde arduino.cc
2. Abre el archivo `arduino_mpu6050.ino` (incluido en esta entrega)
3. Menú Herramientas → Placa: elige tu Arduino (p. ej. Arduino Uno)
4. Menú Herramientas → Puerto: elige el COM donde aparece el Arduino
5. Carga el programa al Arduino (botón Subir)

Si no tienes el sensor o quieres probar la app igual, puedes cargar `arduino_prueba.ino` que envía datos simulados con el mismo formato.

## 5) Instalar Python y las librerías
Si tu PC no tiene Python:
1. Descarga Python 3.11 o superior desde python.org (marca “Add Python to PATH” durante la instalación)
2. Abre la consola (PowerShell)
3. Sitúate en la carpeta del proyecto (la que contiene `Miguel.py`)

Crea un entorno virtual e instala dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si `pip` pide actualizarse, acepta.

## 6) Ejecutar la aplicación desde consola
1. Conecta el Arduino por USB
2. Asegúrate de que el IDE de Arduino y su Monitor Serial estén cerrados (para que el puerto COM no esté ocupado)
3. Desde la consola (PowerShell) en la carpeta del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
python Miguel.py
```

La ventana “Monitor MPU6050 - Arduino” se abrirá.

## 7) Uso básico de la app
- Botón “Conectar”: abre la conexión con el puerto seleccionado.
- “🔄 Buscar”: actualiza la lista de puertos COM disponibles.
- “🔌 Auto”: selecciona y conecta automáticamente al Arduino detectado.
- “🔌 Cerrar”: cierra la conexión serial de forma segura.
- En “Adquisición y Datos” puedes ajustar el tiempo de muestreo (ms), el número de muestras (0 = libre), guardar CSV y generar distintos tipos de gráficas.
	- “💾 Guardar CSV”: te pedirá una carpeta de destino; el nombre del archivo se toma del campo “Nombre datos”.

## 8) Archivos esenciales para la entrega
Incluye solo estos archivos en el zip/entrega:
- `Miguel.py` (aplicación de escritorio)
- `requirements.txt` (lista de librerías Python)
- `arduino_mpu6050/arduino_mpu6050.ino` (código para el Arduino con el MPU6050)
- `arduino_prueba.ino` (opcional: Arduino de prueba con datos simulados)
- `INSTRUCCIONES.md` (este documento)

No es obligatorio incluir archivos temporales, `.venv/`, ni CSV generados.

## 9) Solución de problemas comunes
- No aparece el puerto en la lista: pulsa “🔄 Buscar” y verifica que el cable USB esté bien conectado.
- Error de puerto ocupado: cierra el Monitor Serial del Arduino IDE y vuelve a intentar.
- No ves datos: verifica el cableado del sensor y que el sketch `arduino_mpu6050.ino` está cargado.
- Baudios: deja 9600 salvo que hayas modificado el sketch de Arduino.

## 10) Formato de datos esperado
```
AX:valor,AY:valor,AZ:valor,GX:valor,GY:valor,GZ:valor
```
Ejemplo:
```
AX:0.12,AY:-0.05,AZ:9.78,GX:1.23,GY:-0.45,GZ:0.67
```
/*
 * Código Arduino para MPU6050
 * Conectar:
 * VCC -> 5V o 3.3V
 * GND -> GND
 * SCL -> A5 (Pin analógico 5)
 * SDA -> A4 (Pin analógico 4)
 */

#include <Wire.h>

const int MPU = 0x68; // Dirección I2C del MPU6050

// Variables para almacenar los datos
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  // Registro PWR_MGMT_1
  Wire.write(0);     // Establecer a cero (despertar el MPU6050)
  Wire.endTransmission(true);
  
  Serial.println("MPU6050 Inicializado");
  delay(1000);
}

void loop() {
  // Leer datos del acelerómetro y giroscopio
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // Comenzar con el registro 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 14, true); // Solicitar un total de 14 registros
  
  // Leer los datos
  AcX = Wire.read() << 8 | Wire.read(); // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY = Wire.read() << 8 | Wire.read(); // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ = Wire.read() << 8 | Wire.read(); // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp = Wire.read() << 8 | Wire.read(); // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  GyX = Wire.read() << 8 | Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY = Wire.read() << 8 | Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ = Wire.read() << 8 | Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  
  // Convertir los datos crudos a unidades físicas
  float accel_x = AcX / 16384.0; // ±2g
  float accel_y = AcY / 16384.0;
  float accel_z = AcZ / 16384.0;
  
  float gyro_x = GyX / 131.0; // ±250°/s
  float gyro_y = GyY / 131.0;
  float gyro_z = GyZ / 131.0;
  
  // Enviar datos en formato que Python puede parsear
  Serial.print("AX:");
  Serial.print(accel_x);
  Serial.print(",AY:");
  Serial.print(accel_y);
  Serial.print(",AZ:");
  Serial.print(accel_z);
  Serial.print(",GX:");
  Serial.print(gyro_x);
  Serial.print(",GY:");
  Serial.print(gyro_y);
  Serial.print(",GZ:");
  Serial.println(gyro_z);
  
  delay(50); // Enviar datos cada 50ms (20Hz)
}
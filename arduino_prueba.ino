/*
 * Código de prueba simple para Arduino
 * Use este código si el MPU6050 no funciona
 * Solo envía datos de prueba para verificar la comunicación serial
 */

void setup() {
  Serial.begin(9600);
  Serial.println("Arduino Iniciado - Codigo de Prueba");
  delay(1000);
}

void loop() {
  // Enviar datos de prueba en formato MPU6050
  Serial.print("AX:");
  Serial.print(random(-100, 100) / 100.0);
  Serial.print(",AY:");
  Serial.print(random(-100, 100) / 100.0);
  Serial.print(",AZ:");
  Serial.print(9.8 + random(-50, 50) / 100.0);
  Serial.print(",GX:");
  Serial.print(random(-100, 100) / 10.0);
  Serial.print(",GY:");
  Serial.print(random(-100, 100) / 10.0);
  Serial.print(",GZ:");
  Serial.println(random(-100, 100) / 10.0);
  
  delay(100); // Enviar datos cada 100ms
}
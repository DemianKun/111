#include <WiFi.h>
#include <HTTPClient.h>
#include <HX711.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// --- Configuración de Red (Tus datos) ---
const char* ssid = "TP-Link_B55C";
const char* password = "Psicodrama81";
const char* serverUrl = "http://192.168.0.131:8000/api/sensores";

// --- Configuración Temperatura (Pin 15) ---
const int ONE_WIRE_BUS = 15;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// --- Configuración 6 Básculas (Tus Pines Exactos) ---
HX711 scale1, scale2, scale3, scale4, scale5, scale6;

const int DOUT1 = 23, SCK1 = 22; 
const int DOUT2 = 21, SCK2 = 19;
const int DOUT3 = 18, SCK3 = 5;  
const int DOUT4 = 17, SCK4 = 16;
const int DOUT5 = 27, SCK5 = 26; 
const int DOUT6 = 32, SCK6 = 33;

// Factores de Calibración (Ajustar con pesas reales)
float cal_factors[] = {-1000.0, -10000.0, -10000.0, -10000.0, -10000.0, -10000.0};

unsigned long lastTime = 0;
const unsigned long timerDelay = 30000;
// Envío cada 3 seg (Tiempo Real)

void setup() {
  Serial.begin(115200);
  
  // Conexión WiFi con Reintento Automático
  WiFi.begin(ssid, password);
  Serial.print("Conectando a Red KitchenOS");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Conectado. IP: " + WiFi.localIP().toString());

  // Inicialización de Básculas
  scale1.begin(DOUT1, SCK1); scale1.set_scale(cal_factors[0]); scale1.tare();
  scale2.begin(DOUT2, SCK2); scale2.set_scale(cal_factors[1]); scale2.tare();
  scale3.begin(DOUT3, SCK3); scale3.set_scale(cal_factors[2]); scale3.tare();
  scale4.begin(DOUT4, SCK4); scale4.set_scale(cal_factors[3]); scale4.tare();
  scale5.begin(DOUT5, SCK5); scale5.set_scale(cal_factors[4]); scale5.tare();
  scale6.begin(DOUT6, SCK6); scale6.set_scale(cal_factors[5]); scale6.tare();
  
  sensors.begin();
  Serial.println("🛡️ Sensores calibrados y listos para auditoría.");
}

void loop() {
  if ((millis() - lastTime) > timerDelay) {
    if(WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      
      // 1. Lectura de Temperatura
      sensors.requestTemperatures(); 
      float tempC = sensors.getTempCByIndex(0);
      
      // 2. Lectura de Pesos con Filtro de Estabilidad (Promedio de 5)
      // Usamos max(0.0f, ...) para limpiar el ruido negativo
      float pesos[6];
      pesos[0] = max(0.0f, scale1.get_units(5));
      pesos[1] = max(0.0f, scale2.get_units(5));
      pesos[2] = max(0.0f, scale3.get_units(5));
      pesos[3] = max(0.0f, scale4.get_units(5));
      pesos[4] = max(0.0f, scale5.get_units(5));
      pesos[5] = max(0.0f, scale6.get_units(5));
      
      // 3. Empaquetado JSON Empresarial (MODIFICADO PARA QUITAR EL ERROR 422)
      StaticJsonDocument<256> doc;
      doc["temp_camara"] = (tempC == -127.0) ? 0 : tempC; // Error de sensor Dallas
      
      // Enviamos el formato "plano" exactamente como lo pide backend/main.py
      doc["peso_b1"] = pesos[0];
      doc["peso_b2"] = pesos[1];
      doc["peso_b3"] = pesos[2];
      doc["peso_b4"] = pesos[3];
      doc["peso_b5"] = pesos[4];
      doc["peso_b6"] = pesos[5];

      String jsonOutput;
      serializeJson(doc, jsonOutput);
      
      // 4. Envío de Telemetría
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      
      int httpResponseCode = http.POST(jsonOutput);
      if (httpResponseCode > 0) {
        Serial.printf("📡 Datos enviados [%d]\n", httpResponseCode);
      } else {
        Serial.printf("❌ Fallo de envío: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end();
      
    } else {
      Serial.println("📡 WiFi perdido. Reintentando...");
      WiFi.reconnect();
    }
    lastTime = millis();
  }
}
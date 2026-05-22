#include "HX711.h"
#include <WiFi.h>
#include <HTTPClient.h>

// =====================
// Wi-Fi 정보
// =====================
const char* ssid = "IPHONE";
const char* password = "13871387";

// =====================
// Flask 서버 주소
// 노트북의 IP 주소로 변경 필요
// =====================
const char* serverUrl = "http://172.20.10.5:5000/data";

// =====================
// HX711 핀 번호
// =====================
const int DT_PIN_1  = 34;
const int SCK_PIN_1 = 18;

const int DT_PIN_2  = 33;
const int SCK_PIN_2 = 32;

const int DT_PIN_3  = 25;
const int SCK_PIN_3 = 26;

const int DT_PIN_4  = 14;
const int SCK_PIN_4 = 27;

// =====================
// HX711 객체 생성
// =====================
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

void setup() {
  Serial.begin(115200);
  
  // HX711 시작
  scale1.begin(DT_PIN_1, SCK_PIN_1);
  scale2.begin(DT_PIN_2, SCK_PIN_2);
  scale3.begin(DT_PIN_3, SCK_PIN_3);
  scale4.begin(DT_PIN_4, SCK_PIN_4);
  
  Serial.println("HX711 initialized.");
  
  // Wi-Fi 연결
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("Connected SSID: ");
  Serial.println(WiFi.SSID());
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("Ready!");
}

void loop() {
  long r1 = 0;
  long r2 = 0;
  long r3 = 0;
  long r4 = 0;
  
  // 각 로드셀 raw 값 읽기
  if (scale1.is_ready()) {
    r1 = scale1.read();
  } else {
    Serial.println("HX711-1 not ready");
  }
  
  if (scale2.is_ready()) {
    r2 = scale2.read();
  } else {
    Serial.println("HX711-2 not ready");
  }
  
  if (scale3.is_ready()) {
    r3 = scale3.read();
  } else {
    Serial.println("HX711-3 not ready");
  }
  
  if (scale4.is_ready()) {
    r4 = scale4.read();
  } else {
    Serial.println("HX711-4 not ready");
  }
  
  long total = r1 + r2 + r3 + r4;
  
  // 시리얼 모니터 출력
  Serial.print("Loadcell 1: ");
  Serial.print(r1);
  Serial.print(" | Loadcell 2: ");
  Serial.print(r2);
  Serial.print(" | Loadcell 3: ");
  Serial.print(r3);
  Serial.print(" | Loadcell 4: ");
  Serial.print(r4);
  Serial.print(" | Total: ");
  Serial.println(total);
  
  // Flask 서버로 전송
  sendData(r1, r2, r3, r4, total);
  
  delay(1000);
}

void sendData(long r1, long r2, long r3, long r4, long total) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String jsonData = "{";
    jsonData += "\"loadcell1\":" + String(r1) + ",";
    jsonData += "\"loadcell2\":" + String(r2) + ",";
    jsonData += "\"loadcell3\":" + String(r3) + ",";
    jsonData += "\"loadcell4\":" + String(r4) + ",";
    jsonData += "\"total\":" + String(total);
    jsonData += "}";
    
    int httpResponseCode = http.POST(jsonData);
    
    Serial.print("Sent data: ");
    Serial.println(jsonData);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    
    http.end();
  } else {
    Serial.println("WiFi disconnected. Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
  }
}

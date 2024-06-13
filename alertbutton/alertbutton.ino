#include <WiFi.h>
#include <HTTPClient.h>

#define button 4

// const char* ssid = "ITI_Pladaw";
// const char* password = "forITIteacher";
const char* ssid = "ARK";
const char* password = "beerzz12";
// const char* ssid = "Ark[]-2.4G";
// const char* password = "X1209701998690";
// const char* ssid = "TP_Armmy";
// const char* password = "123456780";
const char* serverUrl = "https://5c1pk0wg-8000.asse.devtunnels.ms/button";

HTTPClient http;

void setup() {
  Serial.begin(115200);
  while(!Serial);
  Serial.flush();
  
  pinMode(button, INPUT_PULLUP);
  
  connectToWiFi();
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
}

void loop() {
  if(digitalRead(button) == LOW){
    
    // สร้าง JSON object เพื่อส่งไปยัง FastAPI
    String jsonPayload = "{\"is_pressed\": true}";
    
    int httpResponseCode = http.POST(jsonPayload);
    if(httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
    Serial.println("SEND");
    delay(10); // รอ 1 วินาทีก่อนส่งข้อมูลใหม่
  }
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Attempting to connect to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

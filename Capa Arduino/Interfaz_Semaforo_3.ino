#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "BUAP_Trabajadores";
const char *password = "BuaPW0rk.2017";

// Asignación de pines
#define PIN_LED_VERDE     21  // Salida LED VERDE
#define PIN_LED_AMARILLO  22  // Salida LED AMARILLO
#define PIN_LED_ROJO      23  // Salida LED ROJO

// Crear un servidor web en el puerto 80
WebServer server(80);

// Variables de estado de los LEDs (true = encendido, false = apagado)
bool estadoVerde = false;
bool estadoAmarillo = false;
bool estadoRojo = false;

// Variable de control para el bucle del semáforo
bool semaforoActivo = false;

// Variables tiempo de los LEDs
int tiempoVerde = 3;      // valor por defecto (segundos)
int tiempoAmarillo = 1;   // valor por defecto (segundos)
int tiempoRojo = 2;       // valor por defecto (segundos)

// Función para controlar el estado físico del LED según la lógica inversa
void controlarLED(int pin, bool encendido) {
  // LÓGICA INVERSA: HIGH = APAGADO, LOW = ENCENDIDO
  digitalWrite(pin, encendido ? LOW : HIGH);
}

void setup() {
  // Inicialización de la comunicación serie
  Serial.begin(115200);

  // Configuración de pines
  pinMode(PIN_LED_VERDE, OUTPUT);     // Salida LED VERDE
  pinMode(PIN_LED_AMARILLO, OUTPUT);  // Salida LED AMARILLO
  pinMode(PIN_LED_ROJO, OUTPUT);      // Salida LED ROJO
  
  // Apagar todos los LEDs al inicio (HIGH = APAGADO con lógica inversa)
  controlarLED(PIN_LED_VERDE, false);
  controlarLED(PIN_LED_AMARILLO, false);
  controlarLED(PIN_LED_ROJO, false);
    
  // Conectar a la red Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("¡Conectado!");
  Serial.println(WiFi.localIP()); 

  // Rutas para controlar el LED VERDE (toggle)
  server.on("/led/verde/toggle", HTTP_GET, []() {
    estadoVerde = !estadoVerde;
    controlarLED(PIN_LED_VERDE, estadoVerde);
    server.send(200, "text/plain", estadoVerde ? "LED Verde Encendido" : "LED Verde Apagado");
  });

  // Rutas para controlar el LED AMARILLO (toggle)
  server.on("/led/amarillo/toggle", HTTP_GET, []() {
    estadoAmarillo = !estadoAmarillo;
    controlarLED(PIN_LED_AMARILLO, estadoAmarillo);
    server.send(200, "text/plain", estadoAmarillo ? "LED Amarillo Encendido" : "LED Amarillo Apagado");
  });

  // Rutas para controlar el LED ROJO (toggle)
  server.on("/led/rojo/toggle", HTTP_GET, []() {
    estadoRojo = !estadoRojo;
    controlarLED(PIN_LED_ROJO, estadoRojo);
    server.send(200, "text/plain", estadoRojo ? "LED Rojo Encendido" : "LED Rojo Apagado");
  });

  // Rutas para manejar el semáforo automático
  server.on("/rutina/semaforo/on", HTTP_GET, []() {
    semaforoActivo = true;
    server.send(200, "text/plain", "Semáforo iniciado");
  });

  server.on("/rutina/semaforo/off", HTTP_GET, []() {
    semaforoActivo = false;
    // Apagar todos los LEDs al detener (opcional, según tu necesidad)
    controlarLED(PIN_LED_VERDE, false);
    controlarLED(PIN_LED_AMARILLO, false);
    controlarLED(PIN_LED_ROJO, false);
    server.send(200, "text/plain", "Semáforo detenido");
  });

  // Ruta para ajustar tiempo del verde
  server.on("/tiempo/verde", HTTP_GET, []() {
    if (server.hasArg("tiempo")) {
      int nuevoTiempo = server.arg("tiempo").toInt();
      if (nuevoTiempo >= 1 && nuevoTiempo <= 10) {
        tiempoVerde = nuevoTiempo;
        server.send(200, "text/plain", "Tiempo del verde actualizado a " + String(tiempoVerde) + " segundos");
      } else {
        server.send(400, "text/plain", "El tiempo debe estar entre 1 y 10 segundos");
      }
    } else {
      server.send(400, "text/plain", "Falta argumento 'tiempo'");
    }
  });

  // Ruta para ajustar tiempo del amarillo
  server.on("/tiempo/amarillo", HTTP_GET, []() {
    if (server.hasArg("tiempo")) {
      int nuevoTiempo = server.arg("tiempo").toInt();
      if (nuevoTiempo >= 1 && nuevoTiempo <= 10) {
        tiempoAmarillo = nuevoTiempo;
        server.send(200, "text/plain", "Tiempo del amarillo actualizado a " + String(tiempoAmarillo) + " segundos");
      } else {
        server.send(400, "text/plain", "El tiempo debe estar entre 1 y 10 segundos");
      }
    } else {
      server.send(400, "text/plain", "Falta argumento 'tiempo'");
    }
  });

  // Ruta para ajustar tiempo del rojo
  server.on("/tiempo/rojo", HTTP_GET, []() {
    if (server.hasArg("tiempo")) {
      int nuevoTiempo = server.arg("tiempo").toInt();
      if (nuevoTiempo >= 1 && nuevoTiempo <= 10) {
        tiempoRojo = nuevoTiempo;
        server.send(200, "text/plain", "Tiempo del rojo actualizado a " + String(tiempoRojo) + " segundos");
      } else {
        server.send(400, "text/plain", "El tiempo debe estar entre 1 y 10 segundos");
      }
    } else {
      server.send(400, "text/plain", "Falta argumento 'tiempo'");
    }
  });
  
  // Iniciar el servidor
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  // Maneja las solicitudes entrantes
  server.handleClient();

  if (semaforoActivo) {
    ejecutarSemaforo();
  }
}

// Función que ejecuta la secuencia del semáforo
void ejecutarSemaforo() {
  // Verde parpadea 3 veces (con verificación constante de semaforoActivo)
  for (int i = 0; i < 3 && semaforoActivo; i++) {
    // Encendido por el tiempo especificado (LOW = ENCENDIDO)
    controlarLED(PIN_LED_VERDE, true);
    for (int j = 0; j < tiempoVerde * 100 && semaforoActivo; j++) {
      delay(10); // 10ms * 100 = 1 segundo, * tiempoVerde = tiempo total
      server.handleClient(); // Sigue manejando solicitudes durante el delay
    }
    
    // Apagado por 1 segundo entre parpadeos (HIGH = APAGADO)
    controlarLED(PIN_LED_VERDE, false);
    for (int j = 0; j < 100 && semaforoActivo; j++) {
      delay(10); // 10ms * 100 = 1 segundo
      server.handleClient(); // Sigue manejando solicitudes durante el delay
    }
  }

  // Amarillo (con verificación constante de semaforoActivo)
  if (semaforoActivo) {
    controlarLED(PIN_LED_AMARILLO, true);
    for (int i = 0; i < tiempoAmarillo * 100 && semaforoActivo; i++) {
      delay(10); // 10ms * 100 = 1 segundo, * tiempoAmarillo = tiempo total
      server.handleClient(); // Sigue manejando solicitudes durante el delay
    }
    controlarLED(PIN_LED_AMARILLO, false);
  }

  // Rojo (con verificación constante de semaforoActivo)
  if (semaforoActivo) {
    controlarLED(PIN_LED_ROJO, true);
    for (int i = 0; i < tiempoRojo * 100 && semaforoActivo; i++) {
      delay(10); // 10ms * 100 = 1 segundo, * tiempoRojo = tiempo total
      server.handleClient(); // Sigue manejando solicitudes durante el delay
    }
    controlarLED(PIN_LED_ROJO, false);
  }

  // Pequeña pausa antes de repetir (con verificación)
  if (semaforoActivo) {
    for (int i = 0; i < 50 && semaforoActivo; i++) {
      delay(10); // 10ms * 50 = 0.5 segundos
      server.handleClient(); // Sigue manejando solicitudes durante el delay
    }
  }
}
#include <SoftwareSerial.h>

#define SIM_RX 10
#define SIM_TX 11

SoftwareSerial sim(SIM_RX, SIM_TX);

const unsigned long BAUD_RATE = 9600;
const int MAX_MESSAGE_LENGTH = 500;
const int COMMAND_TIMEOUT = 30000;

String inputBuffer = "";
bool isProcessing = false;

void setup() {
  // CRITICAL: Start serial FIRST
  Serial.begin(BAUD_RATE);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  // Immediate feedback
  Serial.println("SYSTEM:STARTING");
  Serial.flush();
  
  sim.begin(BAUD_RATE);
  delay(2000);
  
  initializeSIM800L();
  
  Serial.println("SYSTEM:READY");
  Serial.flush();
}

void loop() {
  // Process Serial commands
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        processCommand(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
      
      if (inputBuffer.length() > MAX_MESSAGE_LENGTH + 50) {
        Serial.println("ERROR:COMMAND_TOO_LONG");
        Serial.flush();
        inputBuffer = "";
      }
    }
  }
  
  // Consume SIM800L responses silently
  while (sim.available()) {
    sim.read();
  }
  
  delay(10);
}

void initializeSIM800L() {
  Serial.println("STATUS:INITIALIZING");
  Serial.flush();
  
  // Turn off echo
  sendATCommand("ATE0", 800);
  
  // Test AT
  if (!sendATCommand("AT", 800)) {
    Serial.println("ERROR:NO_RESPONSE");
    Serial.flush();
    return;
  }
  
  Serial.println("STATUS:CHECKING_SIM");
  Serial.flush();
  
  String simResponse = sendATCommand("AT+CPIN?", 1000);
  if (simResponse.indexOf("READY") < 0) {
    Serial.println("ERROR:NO_SIM");
    Serial.flush();
    return;
  }
  
  Serial.println("STATUS:CHECKING_SIGNAL");
  Serial.flush();
  
  String signalResponse = sendATCommand("AT+CSQ", 1000);
  if (signalResponse.length() > 0) {
    int signalStart = signalResponse.indexOf("+CSQ: ") + 6;
    int signalEnd = signalResponse.indexOf(",", signalStart);
    if (signalStart > 6 && signalEnd > signalStart) {
      String signalStr = signalResponse.substring(signalStart, signalEnd);
      Serial.print("SIGNAL:");
      Serial.println(signalStr);
      Serial.flush();
    }
  }
  
  Serial.println("STATUS:REGISTERING_NETWORK");
  Serial.flush();
  
  if (!checkNetworkRegistration()) {
    Serial.println("ERROR:NO_NETWORK");
    Serial.flush();
    return;
  }
  
  // Set SMS text mode
  sendATCommand("AT+CMGF=1", 800);
  
  Serial.println("STATUS:INITIALIZED");
  Serial.flush();
}

bool checkNetworkRegistration() {
  for (int i = 0; i < 20; i++) {
    String response = sendATCommand("AT+CREG?", 500);
    
    if (response.indexOf(",1") > 0 || response.indexOf(",5") > 0) {
      Serial.println("STATUS:NETWORK_REGISTERED");
      Serial.flush();
      return true;
    }
    
    delay(1000);
  }
  
  return false;
}

String sendATCommand(String cmd, int waitTime) {
  sim.println(cmd);
  delay(waitTime);
  
  String response = "";
  unsigned long startTime = millis();
  
  while (millis() - startTime < waitTime) {
    while (sim.available()) {
      response += char(sim.read());
    }
  }
  
  return response;
}

void processCommand(String command) {
  command.trim();
  
  // Acknowledge receipt immediately
  Serial.print("DEBUG:RECEIVED:");
  Serial.println(command);
  Serial.flush();
  
  if (command.startsWith("SEND:")) {
    String remaining = command.substring(5);
    int delimPos = remaining.indexOf(':');
    
    if (delimPos > 0) {
      String phone = remaining.substring(0, delimPos);
      String message = remaining.substring(delimPos + 1);
      
      if (phone.length() > 0 && message.length() > 0) {
        sendSMS(phone, message);
      } else {
        Serial.println("ERROR:INVALID_FORMAT");
        Serial.flush();
      }
    } else {
      Serial.println("ERROR:INVALID_FORMAT");
      Serial.flush();
    }
  }
  else if (command == "STATUS") {
    if (isProcessing) {
      Serial.println("STATUS:BUSY");
    } else {
      Serial.println("STATUS:READY");
    }
    Serial.flush();
  }
  else if (command == "SIGNAL") {
    reportSignalQuality();
  }
  else if (command == "NETWORK") {
    if (checkNetworkRegistration()) {
      Serial.println("OK:NETWORK_REGISTERED");
    } else {
      Serial.println("ERROR:NO_NETWORK");
    }
    Serial.flush();
  }
  else if (command == "RESET") {
    Serial.println("STATUS:RESETTING");
    Serial.flush();
    initializeSIM800L();
    Serial.println("OK:RESET_COMPLETE");
    Serial.flush();
  }
  else if (command == "PING") {
    Serial.println("OK:PONG");
    Serial.flush();
  }
  else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
    Serial.flush();
  }
}

void sendSMS(String phoneNumber, String message) {
  if (isProcessing) {
    Serial.println("ERROR:BUSY");
    Serial.flush();
    return;
  }
  
  isProcessing = true;
  Serial.println("STATUS:SENDING");
  Serial.flush();
  
  // Check network
  if (!checkNetworkRegistration()) {
    Serial.println("ERROR:NO_NETWORK");
    Serial.flush();
    isProcessing = false;
    return;
  }
  
  // Set text mode
  sendATCommand("AT+CMGF=1", 500);
  
  // Start SMS
  String response = sendATCommand("AT+CMGS=\"" + phoneNumber + "\"", 1000);
  
  if (response.indexOf(">") < 0) {
    Serial.println("ERROR:SMS_INIT_FAILED");
    Serial.flush();
    isProcessing = false;
    return;
  }
  
  // Send message content
  sim.print(message);
  delay(100);
  sim.write(26);  // Ctrl+Z
  
  // Wait for response
  unsigned long startTime = millis();
  String smsResponse = "";
  bool success = false;
  
  while (millis() - startTime < COMMAND_TIMEOUT) {
    while (sim.available()) {
      char c = sim.read();
      smsResponse += c;
      
      if (smsResponse.indexOf("+CMGS:") >= 0) {
        success = true;
        break;
      }
      
      if (smsResponse.indexOf("ERROR") >= 0) {
        Serial.println("ERROR:SMS_SEND_FAILED");
        Serial.flush();
        isProcessing = false;
        return;
      }
    }
    
    if (success) break;
    delay(100);
  }
  
  if (success) {
    Serial.println("OK:SMS_SENT");
  } else {
    Serial.println("ERROR:TIMEOUT");
  }
  Serial.flush();
  
  isProcessing = false;
}

void reportSignalQuality() {
  String response = sendATCommand("AT+CSQ", 500);
  
  if (response.length() > 0) {
    int signalStart = response.indexOf("+CSQ: ") + 6;
    int signalEnd = response.indexOf(",", signalStart);
    
    if (signalStart > 6 && signalEnd > signalStart) {
      String signalStr = response.substring(signalStart, signalEnd);
      int signal = signalStr.toInt();
      Serial.print("SIGNAL:");
      Serial.println(signal);
      Serial.flush();
    } else {
      Serial.println("ERROR:NO_SIGNAL_DATA");
      Serial.flush();
    }
  } else {
    Serial.println("ERROR:NO_RESPONSE");
    Serial.flush();
  }
}
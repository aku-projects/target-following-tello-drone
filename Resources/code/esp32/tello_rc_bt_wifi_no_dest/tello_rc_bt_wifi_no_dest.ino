#include "BluetoothSerial.h"
#include <Tello.h>


#define RXD2 16
#define TXD2 17
#define INPUT_SIZE 30

BluetoothSerial BT_SERIAL;
Tello tello;


const char * networkName = "TELLO-XXXXX";
const char * networkPswd = "";
String BT_CALLBACK = "";
String command = "";
char input;
int controlmode = 0;
boolean connected = false;




void connectToWiFi(const char * ssid, const char * pwd) 
{
  Serial.println("Connecting to WiFi network: " + String(ssid));
  BT_SERIAL.println("Connecting to WiFi network: " + String(ssid));
  WiFi.disconnect(true);
  WiFi.onEvent(WiFiEvent);
  WiFi.begin(ssid, pwd);
  Serial.println("Waiting for WIFI connection...");
  
}

void WiFiEvent(WiFiEvent_t event) 
{
  switch (event) 
  {
    case SYSTEM_EVENT_STA_GOT_IP:
      Serial.print("WiFi connected! IP address: ");
      Serial.println(WiFi.localIP());
      BT_SERIAL.print("WiFi connected! IP address: ");
      BT_SERIAL.println(WiFi.localIP());
      tello.init();
      delay(1000);
      Serial.println("Speed : "+ tello.getSpeed());
      BT_SERIAL.println("Speed : "+ tello.getSpeed());
      connected = true;
      break;
      
    case SYSTEM_EVENT_STA_DISCONNECTED:
      Serial.println("WiFi lost connection");
      BT_SERIAL.println("WiFi lost connection");
      connected = false;
      break;
  }
}



void BTCallback(esp_spp_cb_event_t event, esp_spp_cb_param_t *param)
{
    if(event == ESP_SPP_SRV_OPEN_EVT)               // CONNECTION STABLISHED
    {
        BT_CALLBACK = "BTonConnect";
    }
    else if(event == ESP_SPP_CLOSE_EVT)             // CONNECTION CLOSED
    {
        ESP.restart();
    }
    else if(event == ESP_SPP_DATA_IND_EVT)          // DATA RECEIVED
    {
        BT_CALLBACK = "BTonReceivedStart";
    }
//    else if(event == ESP_SPP_WRITE_EVT)             // DATA WRITED
//    {
//        BT_CALLBACK = "BTonWrite";
//    }
}


void BTonReceivedStart()
{
    if(BT_SERIAL.available())
    {
        input = BT_SERIAL.read();
        BT_SERIAL.flush();
        switch(input)
        {
         case 0:
          command = "takeoff";
          controlmode = 0;
          break;
         case 1:
          command = "land";
          controlmode = 0;
          break; 
         case 2:
          command = "rotate clockwise";
          controlmode = 0;
          break;
         case 3:
          command = "rotate anticlockwise";
          controlmode = 0;
          break;
         case 4:
          command = "auto";
          controlmode = 1;
          break;
         case 5:
          command = "turn off";
          controlmode = 0;
          break;
         case 6:
          command = "left";
          controlmode = 0;
          break;
         case 7:
          command = "right";
          controlmode = 0;
          break;
         case 8:
          command = "forward";
          controlmode = 0;
          break;
         case 9:
          command = "backward";
          controlmode = 0;
          break;      
        }
    }
}


 
void setup()
{
  
  Serial.begin(115200);
  BT_SERIAL.register_callback(BTCallback);
  BT_SERIAL.begin("ESP32test");
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("Serial Txd is on pin: "+String(TX));
  Serial.println("Serial Rxd is on pin: "+String(RX));
  BT_SERIAL.println("Serial Txd is on pin: "+String(TX));
  BT_SERIAL.println("Serial Rxd is on pin: "+String(RX));
  connectToWiFi(networkName, networkPswd);
}


void automode_run()
{
  while(controlmode)
  {

    if(connected)
    {
      Serial.println("In automode");
      BT_SERIAL.println("In automode");
      Serial2.write("1");
      delay(90);
  
      if (Serial2.available()) 
      {
        char input[INPUT_SIZE + 1];
        byte size = Serial2.readBytes(input, INPUT_SIZE);
        input[size] = 0;

        char* separator = strchr(input, ':');
        if (separator != 0)
        {

            *separator = 0;
            int tagfound = atoi(input);
            Serial.println(tagfound);
            BT_SERIAL.println(tagfound);
            if (tagfound)
            {
              Serial.println(tagfound);
              Serial.println("racoon found!");
              BT_SERIAL.println(tagfound);
              BT_SERIAL.println("racoon found!");
              
            }
            
            ++separator;
            Serial.println(separator);
            BT_SERIAL.println(separator);
            
            if (tagfound && (strcmp( separator, "rc 0 0 0 0" ) == 0))
             {
              Serial.println("Reached destination!"); 
              BT_SERIAL.println("Reached destination!"); 
              //tello.sendCommand("rc 0 0 0 0");
              //controlmode = 0;
              //break;
              
             }
            tello.sendCommand(separator);
//            delay(500);
//            tello.sendCommand("rc 0 0 0 0");
            Serial.println("Sent command");
            BT_SERIAL.println("Sent command");

          }

      }
  }
  if(BT_CALLBACK=="BTonReceivedStart")
   {
    
    BTonReceivedStart();
    Serial.println(command);
    Serial.println(controlmode);
    BT_SERIAL.println(command);
    BT_SERIAL.println(controlmode);
    if (!controlmode)
    {
      tello.sendCommand("rc 0 0 0 0");
      Serial.println("manual overtake");
      BT_SERIAL.println("manual overtake");
      sendcommand(command);
    }
    BT_CALLBACK="";
    }  

  }  
}

void loop()
{ 
    if(BT_CALLBACK=="BTonReceivedStart")
    {
        BTonReceivedStart();
        Serial.println(command);
        Serial.println(controlmode);
        BT_SERIAL.println(command);
        BT_SERIAL.println(controlmode);
        sendcommand(command);
        BT_CALLBACK="";
        if(controlmode)
        {
          automode_run();  
        }
    }
}

void sendcommand(String command)
{
  if (command == "takeoff")
   {
    tello.takeoff(); 
   }
  if (command == "land")
   {
    tello.land(); 
   } 
  if (command == "rotate clockwise")
   {
    tello.rotate_clockwise(30); 
   }
  if (command == "rotate anticlockwise")
   {
    tello.rotate_anticlockwise(30);
   }
  if (command == "turn off")
   {
    tello.turnOff();
   }
  if (command == "left")
   {
    tello.left(30);
   }
  if (command == "right")
   {
    tello.right(30);
   }
  if (command == "forward")
   {
    tello.forward(30);
   }
  if (command == "backward")
   {
    tello.back(30);
   }
    
}

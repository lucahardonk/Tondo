#define shortPress 100
#define longPress 500
#define sensePin A0
#define batteryPin A1
#define calibrationVoltage 1.1
#include <stdio.h>
#include <stdarg.h>

#define relayUp 22
#define relayDown 23

void setup() {
  Serial.begin(115200);
  while(!Serial){}

  setupRelay(relayUp);
  setupRelay(relayDown);
  pinMode(sensePin, INPUT);
  pinMode(batteryPin, INPUT);

}

String keyWord = "";

void loop() {

  if(Serial.available() > 0){
    keyWord = Serial.readStringUntil('\n');

    if(keyWord != ""){
     //keyWord.trim();
     //Serial.println(keyWord);
      
      if(keyWord == "charge"){Serial.print("ok");toggle(relayDown,longPress);toggle(relayDown,longPress);}
      else if(keyWord == "uncharge"){Serial.print("ok");toggle(relayDown,longPress);toggle(relayDown,longPress);}
      else if(keyWord == "up"){Serial.print("ok");toggle(relayUp,shortPress);}
      else if(keyWord == "down"){Serial.print("ok");toggle(relayDown,shortPress);}
      //jjust add ln if not printing a strng, otherwise is implicit
      else if(keyWord == "charger_contact?"){Serial.println(digitalRead(sensePin));}
      else if(keyWord == "battery"){Serial.println(map(analogRead(batteryPin), 0,1024,0,30) + calibrationVoltage);}
    }
  }
  keyWord = "";
  
}

void setupRelay(const int pin)
{
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

void toggle(const int pin,const int time)
{

  digitalWrite(pin, HIGH);
  delay(time);
  digitalWrite(pin, LOW);
  delay(time);

}

void toggle(const int pin1, const int pin2, const int time )
{

  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, HIGH);
  delay(time);
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
  delay(time);

}

float map(float x, int in_min, int in_max, int out_min, int out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

#include "ST7565.h"

#define R_PIN 3
#define G_PIN 10
#define B_PIN 11

ST7565 glcd(9, 8, 7, 6, 5);

String _song, _artist = "";

void setup()   {                
  Serial.begin(9600);

  Serial.print(freeRam());

  // initialize components
  glcd.begin(0x18);
  glcd.display();

  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);

  digitalWrite(R_PIN, HIGH);
  digitalWrite(G_PIN, HIGH);
  digitalWrite(B_PIN, LOW);
  
}


void loop()                     
{
 if(Serial.available()){
  String msgType = Serial.readStringUntil('|');
  if(msgType == "S"){
    _song = Serial.readStringUntil('|');
    _artist = Serial.readStringUntil('\n');
  }else if(msgType == "P"){
    int playing = Serial.parseInt();
    if(playing == 1){
      digitalWrite(G_PIN, LOW);
      digitalWrite(R_PIN, HIGH);
      digitalWrite(B_PIN, HIGH);
    }else{
      digitalWrite(G_PIN, HIGH);
      digitalWrite(R_PIN, LOW);
      digitalWrite(B_PIN, HIGH);
    }
    while(Serial.available()) Serial.read();
  }
    
  updateDisplay(_song, _artist);
 }
  
}

void updateDisplay(String song, String artist){
  glcd.clear();

  song = "Song: " + song;
  artist = "Artist: " + artist;
  
  char os[128];
  char oa[128];

  song.toCharArray(os, 128);
  artist.toCharArray(oa, 128);
  
  glcd.drawstring(0, 0, os);
  glcd.drawstring(0, 4, oa);
  glcd.display();
}

// this handy function will return the number of bytes currently free in RAM, great for debugging!   
int freeRam(void)
{
  extern int  __bss_end; 
  extern int  *__brkval; 
  int free_memory; 
  if((int)__brkval == 0) {
    free_memory = ((int)&free_memory) - ((int)&__bss_end); 
  }
  else {
    free_memory = ((int)&free_memory) - ((int)__brkval); 
  }
  return free_memory; 
} 


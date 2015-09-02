#include "ST7565.h"

#define R_PIN 3
#define G_PIN 10
#define B_PIN 11
#define SCROLL_SPEED 2500

ST7565 glcd(9, 8, 7, 6, 5);

String _song, _artist, _album, _meta = "";
int spos, apos, alpos, mpos = 0;
unsigned long lastmillis;

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
    _song = "Song: " + Serial.readStringUntil('|');
    _artist = "Artist: " + Serial.readStringUntil('|');
    _album = "Album: " + Serial.readStringUntil('\n');
    _meta = "";
    glcd.clear();
    glcd.display();
    spos = 0;
    apos = 0;
    alpos = 0;
    mpos = 0;
    
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
    Serial.read(); //remove newline from buffer
  }else if(msgType == "M"){
    int saved = Serial.parseInt();
    Serial.read(); //remove deliminator
    int liked = Serial.parseInt();
    Serial.read(); //remove newline from buffer
    _meta = "";
    if(saved == 1){
     _meta += "Saved ";
    }
    if(liked == 1){
     _meta += "Liked ";
    }
    mpos = 0;
  }
 }
 if(lastmillis + SCROLL_SPEED <= millis()){
   spos = scrollDisplay(0, _song, spos, false);
   apos = scrollDisplay(2, _artist, apos, false);
   alpos = scrollDisplay(4, _album, alpos, false);
   mpos = scrollDisplay(6, _meta, mpos, true);
   lastmillis = millis();
 }
}

int scrollDisplay(uint8_t line, String s, int pos, bool disp){
  int x = 0;
  char c[128];
  s.toCharArray(c, 128);

  int written = 0;
  int i = pos;
  while (c[i] != '\0') {
    glcd.drawchar(x, line, c[i]);
    i++;
    x += 6; // 6 pixels wide
    if (x + 6 >= LCDWIDTH && c[i] != '\0') {
      if(disp) glcd.display();
      return written+pos+1; //ran out of space, position to start at next time
    }
    written++;
  }
 while(x < LCDWIDTH){
    glcd.drawchar(x, line, ' ');
    x+= 6;
  }
  if(disp) glcd.display();
  return 0; //start at beginning next time
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


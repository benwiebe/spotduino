/*
 * This file is part of Spotduino.
 *
 * Spotduino is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Spotduino is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Spotduino.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "ST7565.h"

//these pins were selected so that they could be PWM-ed
#define R_PIN 3
#define G_PIN 10
#define B_PIN 11

//how often the display text will scroll (ms)
#define SCROLL_SPEED 2500

//Buffer size for scrolling text. 256 seems to work on Uno, this may be different on other boards
#define SCROLL_BUFFER_SIZE 256

//setup lcd
ST7565 glcd(9, 8, 7, 6, 5);

//global vars
String _song, _artist, _album, _meta = "";
int spos, apos, alpos, mpos = 0;
unsigned long lastmillis;

void setup()   {                
  Serial.begin(9600);

  Serial.print(freeRam());

  // initialize components
  glcd.begin(0x18);
  glcd.display();

  //initialize backlight pins
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);

  digitalWrite(R_PIN, HIGH);
  digitalWrite(G_PIN, HIGH);
  digitalWrite(B_PIN, LOW);
  
}


void loop()                     
{
 //if there's serial data we can read
 if(Serial.available()){
  //read until the deliminator
  String msgType = Serial.readStringUntil('|');

  //determine the type of message
  if(msgType == "S"){ //song data
    //read in the information
    _song = "Song: " + Serial.readStringUntil('|');
    _artist = "Artist: " + Serial.readStringUntil('|');
    _album = "Album: " + Serial.readStringUntil('\n');

    if(_song.length() >= SCROLL_BUFFER_SIZE){
      _song = "Song: *TOO LONG*";
    }

    if(_artist.length() >= SCROLL_BUFFER_SIZE){
      _artist = "Artist: *TOO LONG*";
    }

    if(_album.length() >= SCROLL_BUFFER_SIZE){
      _album = "Album: *TOO LONG*";
    }
    
    //reset vars and clear display
    _meta = "";
    glcd.clear();
    glcd.display();
    spos = 0;
    apos = 0;
    alpos = 0;
    mpos = 0;
    
  }else if(msgType == "M"){ //meta data
    //read in data
    int saved = Serial.parseInt();
    Serial.read(); //remove deliminator
    int liked = Serial.parseInt();
    Serial.read(); //remove newline from buffer
    
    //format display string
    _meta = "";
    if(saved == 1){
     _meta += "Saved ";
    }
    if(liked == 1){
     _meta += "Liked ";
    }
    mpos = 0;
  }else if(msgType == "C"){ //color data
    //read data in
    int r = Serial.parseInt(); //red
    Serial.read(); //remove deliminator
    int g = Serial.parseInt(); //green
    Serial.read(); //remove deliminator
    int b = Serial.parseInt(); //blue
    Serial.read(); //remove newline from buffer

    //set the backlight color to the new values
    setBacklightColor(r, g, b);
  }else{
    //if we have an unrecognized command, clean it up as best we can
    Serial.readStringUntil('\n');
  }
 }

 //update the screen if enough time has passed (as set by SCROLL_SPEED)
 if(lastmillis + SCROLL_SPEED <= millis()){
   spos = scrollDisplay(0, _song, spos, false);
   apos = scrollDisplay(2, _artist, apos, false);
   alpos = scrollDisplay(4, _album, alpos, false);
   mpos = scrollDisplay(6, _meta, mpos, true);
   lastmillis = millis();
 }
}

//scrolls a line of text. adapted from the drawstring function in the ST7565 library
int scrollDisplay(uint8_t line, String s, int pos, bool disp){
  int x = 0;
  //convert String to char array
  char c[SCROLL_BUFFER_SIZE];
  s.toCharArray(c, SCROLL_BUFFER_SIZE);

  //draw the string, based on the current position (pos)
  int written = 0;
  int i = pos;
  while (c[i] != '\0') {
    glcd.drawchar(x, line, c[i]);
    i++;
    x += 6; // 6 pixels wide
    if (x + 6 >= LCDWIDTH && c[i] != '\0') { //rand out of room, AND next character isn't a terminator
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

//set the PWM for the display backlight pins
void setBacklightColor(int r, int g, int b){
  analogWrite(R_PIN, r);
  analogWrite(G_PIN, g);
  analogWrite(B_PIN, b);
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


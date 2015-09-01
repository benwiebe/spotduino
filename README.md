# spotduino
Arduino display for currently playing Spotify song (Linux only).

Usage:
- Make sure spotify-client is installed on your computer (Try running 'spotify' in a terminal. If Spotify opens, you're all set).
- Upload the sketch to the Arduino. The Arduino has an ST7565 display attached (see http://www.ladyada.net/learn/lcd/st7565.html).
  Note: RGB backlight pins are defined at the top of the sketch. Change these to match your setup.
- Update the Python script with the correct serial port for your Arduino.
- Run the Python script. The ST7565 should show the default logo and set the backlight to blue. When you play a song through the client,
  the ST7565 will show the currently playing song, its artist, and playing state (reflected by green/red backlight color. RGB displays only.)

Dependencies:
- Adafruit ST7565 library: https://github.com/adafruit/ST7565-LCD

  NOTE: as per http://forums.adafruit.com/viewtopic.php?f=19&t=21376, you may need to change ST7565.cpp. Around line 188, change 

  `updateBoundingBox(x, line*8, x+5, line*8 + 8);`

  to

  `updateBoundingBox(x-5, line*8, x, line*8 + 8);`
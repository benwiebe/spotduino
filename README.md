# spotduino
Arduino display for currently playing Spotify song (Linux only).

Usage:
- Make sure spotify-client is installed on your computer (Try running 'spotify' in a terminal. If Spotify opens, you're all set).
- Upload the sketch to the Arduino. The Arduino has an ST7565 display attached (see http://www.ladyada.net/learn/lcd/st7565.html).
  Note: RGB backlight pins are defined at the top of the sketch. Change these to match your setup.
- Update the Python script with the correct serial port for your Arduino. Also, set the API_ENABLED variable to True or False, depending
  on whether or not you want the script to use the advanced Spotify APIs. This requires configuring the script with valid API key information,
  which can be setup on the Spotify developers website (https://developer.spotify.com/my-applications/). You will then need to upload the PHP
  scripts in /web to a webserver and use them to get your initial auth key (an improved version of these may be available in the future).
- Run the Python script. The ST7565 should show the default logo and set the backlight to blue. When you play a song through the client,
  the ST7565 will show the currently playing song, its artist, and playing state (reflected by green/red backlight color. RGB displays only.)
  If you set API_ENABLED to True, you will be prompted for your auth key. Input the key that was outputted by the PHP scripts and you're all set!


Dependencies:
- Adafruit ST7565 library: https://github.com/adafruit/ST7565-LCD

  NOTE: as per http://forums.adafruit.com/viewtopic.php?f=19&t=21376, you may need to change ST7565.cpp. Around line 188, change 

  `updateBoundingBox(x, line*8, x+5, line*8 + 8);`

  to

  `updateBoundingBox(x-5, line*8, x, line*8 + 8);`

- PySerial: install using `pip install pyserial` or from http://pyserial.sourceforge.net/
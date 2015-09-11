# spotduino
###Arduino display for currently playing Spotify song (Linux only).

##Features:
- Display current song's:
    - Title
    - Artist
    - Album
- Display whether the current song is in the user's library or liked from radio
- Set RGB backlight color based on song
- Display current time

##Usage:
- Make sure spotify-client is installed on your computer (Try running 'spotify' in a terminal. If Spotify opens, you're all set).
- Upload the sketch to the Arduino. The Arduino has an ST7565 display attached (see http://www.ladyada.net/learn/lcd/st7565.html).
  Note: There are multiple configutation options available. See "Configuration Options" below for more info
- Update the Python script with the correct serial port for your Arduino. This port may need to be `chown`-ed to the user who will be running the 
  script, or `chmod`-ed. Otherwise, the script will most likely need sudo. Also, set the API_ENABLED variable to True or False, depending
  on whether or not you want the script to use the advanced Spotify APIs. This requires configuring the script with valid API key information,
  which can be setup on the Spotify developers website (https://developer.spotify.com/my-applications/). You will then need to upload the PHP
  scripts in /web to a webserver and use them to get your initial auth key (an improved version of these may be available in the future).
- Run the Python script. The ST7565 should show the default logo and set the backlight to blue. When you play a song through the client,
  the ST7565 will show the currently playing song, its artist, and set the background depending on the song. (RGB displays only.)
  If you set API_ENABLED to True, you will be prompted for your auth key. Input the key that was outputted by the PHP scripts and you're all set!

##Configuration Options:
 - Python Script
     - ARDUINO_SERIAL_PORT: the serial port used to communicate with the Arduino. 
     - API_ENABLED: sets whether or not to use authenticated Spotify API calls (ie. loading song saved and liked state)
     - API_CLIENT_ID: Spotify app client ID from the developer console
     - API_CLIENT_SECRET: Spotify app secret ID from the developer console
     - API_REDIRECT: URL that displays the auth token (ie. this should be where web/spotduino_auth_redirect.php is hosted)

 - Arduino Sketch
     - R_PIN, G_PIN, B_PIN: the pins that the display's red, green, and blue backlight pins are connected to (these should ideally be PWM pins)
     - SCROLL_SPEED: how often, in milliseconds, the screen is refreshed
     - STRING_BUFFER_SIZE: buffer size for displaying scrolling text. 192 was tested to work on an Uno, but this may be different on different boards depending on how much RAM they have
     - SHOW_SCROLL_ARROWS: whether or not to display scroll status indicator arrows
     - CLOCK_SHOW: set to true/false depending on if you want a clock shown in the bottom right corner of the screen
     - CLOCK_FORMAT: set to 12/24 depending on your preferred clock format (only relevant if CLOCK_SHOW is true)

##Dependencies:
- Adafruit ST7565 library: https://github.com/adafruit/ST7565-LCD

  NOTE: as per http://forums.adafruit.com/viewtopic.php?f=19&t=21376, you may need to change ST7565.cpp. Around line 188, change 

  `updateBoundingBox(x, line*8, x+5, line*8 + 8);`

  to

  `updateBoundingBox(x-5, line*8, x, line*8 + 8);`

- PySerial: install using `pip install pyserial` or from http://pyserial.sourceforge.net/
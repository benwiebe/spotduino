#imports
import json
import urllib2
import subprocess
import serial
import re

#constants
PREFIX_SONG = "S"
PREFIX_PLAYING = "P"

#global vars
s1883 = False
schange = False
playing = 0

#functions
# from http://stackoverflow.com/a/20078869/1896516
def remove_non_ascii(text):
	return ''.join([i if ord(i) < 128 else '\x0E' for i in text])

#begin main program

ser = serial.Serial('/dev/ttyACM0', 9600)

proc = subprocess.Popen(['spotify'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

while True:
	line = proc.stdout.readline()

	if line != '':
		#check if there's a track id in here
		if "track=spotify:track:" in line: 
			schange = True

			before, after = line.split("track=spotify:track:");
			trackid, end = after.split(",", 1);

			print("trackid: " + trackid + "\n");

			spurl="https://api.spotify.com/v1/tracks/" + trackid
			data = json.load(urllib2.urlopen(spurl))

			print("name: " + data["name"] + "\nartist(s): ")

			artstring = ""

			for artist in data["artists"]:
				artstring += artist["name"] + ", "
				print(artist["name"] + ",")

			print("\n")

			artstring = artstring[:-2]
			outstring = PREFIX_SONG + "|" + data["name"] + "|" + artstring + "\n"
			outstring = remove_non_ascii(outstring)
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")

		elif "spirc_manager.cpp:1883" in line:
			s1883 = True;

		elif "spirc_manager.cpp:668" in line:
			if s1883:
				if playing: schange = False
				playing = 1
				s1883 = False
			else:
				if not schange:
					playing = 0

				schange = False

			print("Playing: ")
			print(playing)
			print("\n")

			outstring = PREFIX_PLAYING + "|" + str(playing) + "\n"
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")

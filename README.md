# Raspberry Pi Spotify Server
Local Spotify Server running on Raspberry Pi (3+) controlled by Spotify mobile app.
It plays music on audio Jack output. Doesn't need Monitor to be plugged in.

![RealWorld example](https://github.com/igrek51/raspberry-spoti-server/blob/master/img/spoti-server-picture.jpg?raw=true)  

External LEDs indicate status:
- Green Diode - blinking means waiting for pulseaudio sink (Spotify paused), solid light means Spotify is playing
- Red Diode - light on when Raspbery is powered

Button - clicked 3 times in a row initiates shutdown

## Setup

1. Flash official RaspiOS `2020-12-02-raspios-buster-armhf.img` on SD.
2. Boot Raspberry, let it reboot (expand filesystem), configure WiFi, user password.
3. Enable SSH: `sudo raspi-config` / Interface Options / SSH
4. Change password: `sudo passwd pi`
4. On host: Run `./push.sh` to transfer files
5. `ssh pi@192.168.0.51`, run `~/init/init.sh`
6. On Raspberry: select "AV Jack" as main audio output.
7. Install Spotify app on chromium: open.spotify.com
8. Copy spotify app id to /home/pi/.config/autostart/spoti.desktop
9. Pinout:
	- PIN1 (3v3) -> LED RED (+) -> LED RED (-) -> resistor (1k) -> PIN 39 (GND)
	- PIN3 (GPIO 2) -> Button (1) -> Button (2) -> PIN 9 (GND)
	- PIN11 (GPIO 17) -> resistor (1k) -> LED GREEN (+) -> LED GREEN (-) -> PIN 6 (GND)

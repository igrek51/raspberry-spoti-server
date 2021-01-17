#!/bin/bash
set -ex
cd "$(dirname "$0")"

# Ensure we are on Raspberry
if [ -f "/boot/config.txt" ]; then
    echo "/boot/config.txt exists."
else 
    echo "/boot/config.txt does not exist."
    exit 1
fi

sudo cp config.txt /boot/config.txt
sudo cp /boot/cmdline.txt cmdline.txt.bak
#sudo cp cmdline.txt /boot/cmdline.txt

# Debugging tools
cp tubular.wav /home/pi/
cp mp3.mp3 /home/pi/
cp pulseaudio-fuckup.sh /home/pi/

sudo apt update
sudo apt install -y vim htop iotop wmctrl playerctl

pip3 install -r /home/pi/init/requirements.txt

# Setup chromium media edition
mkdir -p /home/pi/tmp
cd /home/pi/tmp
curl -fsSL https://pi.vpetkov.net -o ventz-media-pi
sh ventz-media-pi

# Configure autostart apps
mkdir -p /home/pi/.config/autostart

cat << 'EOF' > /home/pi/.config/autostart/spoti.desktop
[Desktop Entry] 
Type=Application
Type=Application
Exec=/usr/bin/chromium-browser --profile-directory=Default --app-id=pjibgclleladliembfgfagdaldikeohf
#Exec=chromium-browser --user-agent="Mozilla/5.0 (X11; CrOS armv7l 12371.89.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36" open.spotify.com
EOF

cat << 'EOF' > /home/pi/.config/autostart/gpio-controller.desktop
[Desktop Entry] 
Type=Application
Exec=lxterminal -e "python3 -u /home/pi/init/control.py |& tee /home/pi/init/control.log"
EOF

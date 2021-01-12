#!/bin/bash -ex
ssh pi@192.168.0.51 "mkdir -p /home/pi/init"
scp * pi@192.168.0.51:/home/pi/init

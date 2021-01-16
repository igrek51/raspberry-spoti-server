#!/bin/bash -ex
ssh-keygen -f "/home/igrek/.ssh/known_hosts" -R "192.168.0.51"
SSHPASS="PUT_YOUR_PASSWORD_HERE" sshpass -e ssh -o StrictHostKeyChecking=no pi@192.168.0.51 "mkdir -p /home/pi/.ssh"
SSHPASS="PUT_YOUR_PASSWORD_HERE" sshpass -e scp -o StrictHostKeyChecking=no ~/.ssh/id_rsa.pub pi@192.168.0.51:/home/pi/.ssh/authorized_keys

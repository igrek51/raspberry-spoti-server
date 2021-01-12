#!/bin/bash
sleep ${1:-0}
pulseaudio -k
pulseaudio --start --high-priority=yes --realtime=yes

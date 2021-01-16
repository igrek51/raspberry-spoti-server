#!/usr/bin/env python3
from gpiozero import LED, Button
import subprocess
import time
from typing import Optional
import re

from dataclasses import dataclass


@dataclass
class State(object):
    shutdown_counter: int = 0
    shutdown_last_click: int = 0


state = State()
led = LED(17)
button = Button(2)


def shell(cmd: str):
    err_code = shell_error_code(cmd)
    if err_code != 0:
        raise RuntimeError(f'command failed: {cmd}')


def shell_error_code(cmd: str) -> int:
    return subprocess.call(cmd, shell=True)


def shell_output(cmd: str):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    return output.decode('utf-8')


def shutdown():
    print('shutting down...')
    for _ in range(10):
        led.off()
        time.sleep(0.04)
        led.on()
        time.sleep(0.02)
    shell('sudo shutdown -h now')


def check_spotify_sink_playing() -> bool:
    output = shell_output('pacmd list-sink-inputs').strip()
    if output.startswith('0 sink input'):
        return False
    if 'sink-input-by-application-name:Chromium' in output:
        return True
    print('unknown pacmd output')
    return False


def spotify_current_title() -> Optional[str]:
    output = shell_output('DISPLAY=:0 wmctrl -l -x').strip()
    for line in output.splitlines():
        if '.Chromium-browser' in line:
            match = re.search(r'raspberrypi +(.+)$', line)
            if not match:
                print(f'wmctrl output not matched: {line}')
                return None
            title = match.group(1)
            if title == 'Spotify – Web Player':
                return None
            print(f'Spotify playing {title}')
            return title
    print(f'chromium window not found')
    return None


def button_pressed():
    now = time.time()
    if now - state.shutdown_last_click <= 1:
        state.shutdown_counter += 1
    else:
        state.shutdown_counter = 1
    state.shutdown_last_click = time.time()
    print(f'click series: {state.shutdown_counter}')

    if state.shutdown_counter >= 3:
        shutdown()


def button_released():
    pass


def blink_led(period: float, pwm: float = 0.5):
    on_time = period * pwm
    off_time = period - on_time
    led.on()
    time.sleep(on_time)
    if off_time > 0:
        led.off()
        time.sleep(off_time)


def display_green_status():
    song = spotify_current_title()
    if not song:
        sink_exists = check_spotify_sink_playing()
        if sink_exists:
            blink_led(1, pwm=0.5)
        else:
            blink_led(1, pwm=0.2)
    else:
        blink_led(1, pwm=1)


def main():
    led.off()
    button.when_pressed = button_pressed
    button.when_released = button_released

    print('ready to work...')
    try:
        while True:
            display_green_status()

    except KeyboardInterrupt:
        led.off()


main()

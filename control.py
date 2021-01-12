#!/usr/bin/env python3
from gpiozero import LED, Button
import subprocess
import time

from dataclasses import dataclass


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
    for i in range(10):
        led.off()
        time.sleep(0.04)
        led.on()
        time.sleep(0.02)
    shell('sudo shutdown -h now')


def check_spotify_playing() -> bool:
    output = shell_output('pacmd list-sink-inputs').strip()
    if output.startswith('0 sink input'):
        return False
    if 'sink-input-by-application-name:Chromium' in output:
        return True
    print('unknown pacmd output')
    return False


@dataclass
class State(object):
    shutdown_counter: int = 0
    shutdown_last_click: int = 0

state = State()


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


def main():
    led.off()

    button.when_pressed = button_pressed
    button.when_released = button_released

    print('ready to work...')
    try:
        while True:
            is_playing = check_spotify_playing()
            if is_playing:
                led.on()
                time.sleep(1)
            else:
                led.on()
                time.sleep(0.5)
                led.off()
                time.sleep(0.5)

    except KeyboardInterrupt:
        led.off()

main()

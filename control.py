#!/usr/bin/env python3
from gpiozero import LED, Button
import subprocess
import time
from typing import Optional
import re
import asyncio
from dataclasses import dataclass

from unidecode import unidecode


@dataclass
class State(object):
    shutdown_counter: int = 0
    shutdown_last_click: int = 0
    play_last_click: int = 0


state = State()

green_led = LED(17)
blue_led = LED(27)
power_button = Button(2)
play_button = Button(3)


MORSE_CODES = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    " ": "/",
}

MORSE_DOT = 0.1
MORSE_DASH = 3 * MORSE_DOT
MORSE_SIGNAL_BREAK = MORSE_DOT
MORSE_LETTER_BREAK = 3 * MORSE_DOT
MORSE_WORD_BREAK = 7 * MORSE_DOT


def shell(cmd: str):
    err_code = shell_error_code(cmd)
    if err_code != 0:
        raise RuntimeError(f"command failed: {cmd}")


def shell_error_code(cmd: str) -> int:
    return subprocess.call(cmd, shell=True)


def shell_output(cmd: str):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, _ = process.communicate()
    return output.decode("utf-8")


def shutdown():
    print("shutting down...")
    for _ in range(10):
        green_led.off()
        time.sleep(0.04)
        green_led.on()
        time.sleep(0.02)
    shell("sudo shutdown -h now")


def check_spotify_sink_playing() -> bool:
    output = shell_output("pacmd list-sink-inputs").strip()
    if output.startswith("0 sink input"):
        return False
    if "sink-input-by-application-name:Chromium" in output:
        return True
    print("unknown pacmd output")
    return False


def spotify_current_title() -> Optional[str]:
    output = shell_output("DISPLAY=:0 wmctrl -l -x").strip()
    for line in output.splitlines():
        if ".Chromium-browser" in line:
            match = re.search(r"raspberrypi +(.+)$", line)
            if not match:
                print(f"wmctrl output not matched: {line}")
                return None
            title = match.group(1)
            if title == "Spotify – Web Player":
                return None
            return title
    print(f"chromium window not found")
    return None


def power_button_pressed():
    now = time.time()
    if now - state.shutdown_last_click <= 1:
        state.shutdown_counter += 1
    else:
        state.shutdown_counter = 1
    state.shutdown_last_click = time.time()
    print(f"click series: {state.shutdown_counter}")

    if state.shutdown_counter >= 3:
        shutdown()


def play_button_pressed():
    now = time.time()
    if now - state.play_last_click <= 1:
        print('next track')
        shell("playerctl next")
    else:
        print('play/pause')
        shell("playerctl play-pause")
    state.play_last_click = now


def simplify_string(s: str) -> str:
    s = unidecode(s).lower()
    s = s.replace("·", " ")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    s = re.sub(r"  +", " ", s)
    return s


def to_morse(s: str) -> str:
    codes = []
    for c in s:
        if c in MORSE_CODES:
            codes.append(MORSE_CODES[c])
    return " ".join(codes)


async def play_morse(led: LED, code: str):
    for c in code:
        if c == ".":
            blue_led.on()
            await asyncio.sleep(MORSE_DOT)
            blue_led.off()
            await asyncio.sleep(MORSE_SIGNAL_BREAK)
        elif c == "-":
            blue_led.on()
            await asyncio.sleep(MORSE_DASH)
            blue_led.off()
            await asyncio.sleep(MORSE_SIGNAL_BREAK)
        elif c == " ":
            blue_led.off()
            await asyncio.sleep(MORSE_LETTER_BREAK)
        elif c == "/":
            blue_led.off()
            await asyncio.sleep(MORSE_WORD_BREAK)


async def blink_led(led: LED, period: float, pwm: float = 0.5):
    on_time = period * pwm
    off_time = period - on_time
    led.on()
    await asyncio.sleep(on_time)
    if off_time > 0:
        led.off()
        await asyncio.sleep(off_time)


async def display_green_status():
    song = spotify_current_title()
    if not song:
        sink_exists = check_spotify_sink_playing()
        if sink_exists:
            await blink_led(green_led, 1, pwm=0.5)
        else:
            await blink_led(green_led, 1, pwm=0.2)
    else:
        await blink_led(green_led, 1, pwm=1)


async def display_blue_status():
    song = spotify_current_title()
    if song:
        simple_title = simplify_string(song)
        morse = to_morse(simple_title) + " /"
        print(f'Spotify playing "{simple_title}": {morse}')
        await play_morse(blue_led, morse)
    else:
        blue_led.off()
        await asyncio.sleep(3)


def init_led():
    green_led.off()
    blue_led.off()


async def green_loop():
    while True:
        await display_green_status()


async def blue_loop():
    while True:
        await display_blue_status()


async def main_loop():
    await asyncio.gather(
        green_loop(),
        blue_loop(),
    )


def main():
    init_led()
    power_button.when_pressed = power_button_pressed
    play_button.when_pressed = play_button_pressed

    print("ready to work...")
    try:
        asyncio.run(main_loop())

    except KeyboardInterrupt:
        init_led()


main()

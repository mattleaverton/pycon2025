# SPDX-FileCopyrightText: 2024 Matt Leaverton, 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Trigger sounds based on button presses
"""
import board
import audiomp3
from audiopwmio import PWMAudioOut as AudioOut
import audiomixer
import keypad
import time
import digitalio

##
# Output Setup
##
timeout_s = 0.50
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
timeout_led = time.monotonic() + timeout_s
led_value = False

##
# Input Setup
##
button_pins = (board.GP1, board.GP2, board.GP3, board.GP4)
buttons = keypad.Keys(button_pins, value_when_pressed=False, pull=True)

##
# Audio System Setup
##
file_type = ".mp3"
mp3files = [
    ("noot-noot", 6),
    ("mcfoody", 1),
    ("nooo", 1),    
    ("gibberish", 4),
]
file_counter = [0, 0, 0, 0]
audio = AudioOut(board.GP0)

# Initialize MP3 player
mp3 = open(mp3files[0][0] + "-0" + file_type, "rb")
decoder = audiomp3.MP3Decoder(mp3)

mixer = audiomixer.Mixer(voice_count=1, sample_rate=24000, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
active_sound = -1
audio.play(mixer)

while True:
    button = buttons.events.get()   # see if there are any key events
    if button:                      # there are events!
        if button.pressed:
            print("button", button.key_number, "pressed!")

            if mixer.playing and button.key_number == active_sound:
                print("Re-triggered same sound!")
                pass
            else:
                if mixer.playing:
                    print("Stopping current sound!")
                    mixer.stop_voice(0)
                    sound_playing = False

                filename = mp3files[button.key_number][0] + "-" + str(file_counter[button.key_number]) + file_type
                print("Playing:", filename)
                decoder.file = open(filename, "rb")
                mixer.voice[0].play(decoder)

                active_sound = button.key_number
                file_counter[button.key_number] += 1
                if file_counter[button.key_number] >= mp3files[button.key_number][1]:
                    file_counter[button.key_number] = 0

    # Toggle the LED
    if time.monotonic() >= timeout_led:
        led_value = not led_value
        led.value = led_value
        timeout_led = time.monotonic() + timeout_s

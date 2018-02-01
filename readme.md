# Rpi Spectrum Wave
This is a simple python script that can be used to implement music visualisation on 8x8 light matrix (LED matrix) without drivers like HT16K33.

## Requirements
1. Raspberry pi 2/3
2. GPIO pins (16)
3. `.wav` file for music to be played
4. Audio output (speaker/earphone/headphone)
5. ALSA audio plugin for python

## Usage
Assuming you have all the required dependencies, here are the few things that you can tweak in the code to make it more accessible to the project you are trying to use. Also, the following will explain the underlying code which will convert the music into visualisation and output the music simultaneously.

*1. Pin layout*
In the code exists these lines of code at line 8 and 9:
```
row = [40,38,29,36,35,31,33,37]
col = [15,12,18,13,22,11,7,16]
```
These correspond to the GPIO pin outputs that correspond to certain row and column on the display. Hence activating row[0] and col[0] according to their active states will make the LED at {1,1} glow.

*2. Row/column active states*
Here we assume that rows are supposed to be provided with 0V and columns to 5V to keep the LEDs in the reverse bias. However, note that this is just a design decision and keeping both at 0V (no potential difference) may also work.

Consequtively, rows should be at 5V and columns at 0V for LED to light up.


*3. Volume controls*
The code simplifies the volume output by the metric of how many LEDs out of total are glowing in the matrix. However it can be customized to will

*4. waveform creation and rendering*
Waveform is created as follows: The wavfile is read in chunks of 8xN bytes (here 4096) and fast fourier transform is applied on that data. This, chunk is made to go through audio output using the 3.5mm jack port. Then, rendering is done using slices fast enough, multiple times to give illusion of glowing LEDs. However owing to limitations in delay of switching in GPIO, flickering is seen and is inevitable. One may tweak the refresh rates using (line 129). Lowering this value from `30` will provide smoother output on audio but jagged and flickering on screen. The increase however does th opposite.

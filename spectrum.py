import alsaaudio as aa
import wave
import time
from struct import unpack
import numpy as np
import RPi.GPIO as GPIO

row = [40,38,29,36,35,31,33,37]
col = [15,12,18,13,22,11,7,16]
volume = [26,10,24,23,21,19]

matrix    = [0,0,0,0,0,0,0,0]
power     = []
weighting = [2,8,8,16,16,32,32,64] 

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

for rowno in row:
   GPIO.setup(rowno,GPIO.OUT)
   GPIO.output(rowno,GPIO.LOW)
for colno in col:
   GPIO.setup(colno,GPIO.OUT)
   GPIO.output(colno,GPIO.HIGH)
for vl in volume:
   GPIO.setup(vl,GPIO.OUT)
   GPIO.output(vl,GPIO.LOW)
   
time.sleep(1)
#Testing
for rowno in row:
   for colno in col:
      GPIO.output(rowno,GPIO.HIGH)
      GPIO.output(colno,GPIO.LOW)
      time.sleep(.010)
      GPIO.output(rowno,GPIO.LOW)
      GPIO.output(colno,GPIO.HIGH)

for vl in volume:
   GPIO.output(vl,GPIO.HIGH)
   time.sleep(.010)
   GPIO.output(vl,GPIO.LOW)

time.sleep(0.4)
matrix1 =np.array([[1,1,1,1,1,1,1,1],
                   [1,1,1,1,1,1,1,1],
                   [0,0,0,0,0,0,0,0],
                   [0,0,1,0,1,1,1,0],
                   [0,1,0,1,1,0,1,0],
                   [0,1,0,1,1,0,1,0],
                   [0,0,0,0,0,0,0,0],
                   [1,1,1,1,1,1,1,1]],np.int32)

for e in range (100):
   for y in range (0,8):
      for x in range (0,8):
         #print "Vals "+str(matrix1[x][y])
         if matrix1[x][y] == 1:
            #print "Otp at "+str(matrix[x][y])
            GPIO.output(row[y],GPIO.HIGH)
            GPIO.output(col[x],GPIO.LOW)
         time.sleep(0.0002)
      for x in range(0, 7):
         GPIO.output(row[y],GPIO.LOW)
         GPIO.output(col[x],GPIO.HIGH)
      

# Audio setup
wavfile = wave.open('music.wav','r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
print sample_rate
print no_channels
chunk       = 4096 # Use a multiple of 8

# ALSA
output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)

# Return power array index corresponding to a particular frequency
def piff(val):
   return int(2*chunk*val/sample_rate)
   
def calculate_levels(data, chunk,sample_rate):
   global matrix

   # Convert raw data (ASCII string) to numpy array
   data = unpack("%dh"%(len(data)/2),data)
   data = np.array(data, dtype='h')

   # Apply FFT - real data
   fourier=np.fft.rfft(data)
   # Remove last element in array to make it the same size as chunk
   fourier=np.delete(fourier,len(fourier)-1)
   # Find average 'amplitude' for specific frequency ranges in Hz
   power = np.abs(fourier)   
   matrix[0]= int(np.mean(power[piff(0)    :piff(156):1]))
   matrix[1]= int(np.mean(power[piff(156)  :piff(313):1]))
   matrix[2]= int(np.mean(power[piff(313)  :piff(625):1]))
   matrix[3]= int(np.mean(power[piff(625)  :piff(1250):1]))
   matrix[4]= int(np.mean(power[piff(1250) :piff(2500):1]))
   matrix[5]= int(np.mean(power[piff(2500) :piff(5000):1]))
   matrix[6]= int(np.mean(power[piff(5000) :piff(10000):1]))
   matrix[7]= int(np.mean(power[piff(10000):piff(20000):1]))

   # Tidy up column values for the LED matrix
   matrix=np.divide(np.multiply(matrix,weighting),1000000)
   # Set floor at 0 and ceiling at 8 for LED matrix
   matrix=matrix.clip(0,8)
   return matrix


# Start reading .wav file  
data = wavfile.readframes(chunk)
# Loop while audio data present
while data!='':
   output.write(data)   
   matrix=calculate_levels(data, chunk,sample_rate)
   volume_ = 0
   for y in range (0,8):
      volume_ = volume_ + matrix[y]

   volume_ = volume_*(6.0/64.0)
   for vl in range (0,int(volume_)):
      GPIO.output(volume[vl],GPIO.HIGH)
   for vl in range (int(volume_)+1,6):
      GPIO.output(volume[vl],GPIO.LOW)
   for e in range (30):
      for y in range (0,8):
         for x in range(0, matrix[y]):
              GPIO.output(row[y],GPIO.HIGH)
              GPIO.output(col[x],GPIO.LOW)
         time.sleep(.0001)
         for x in range(0, 8):
              GPIO.output(row[y],GPIO.LOW)
              GPIO.output(col[x],GPIO.HIGH)
   data = wavfile.readframes(chunk)
   

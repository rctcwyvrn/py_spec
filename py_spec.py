from scipy.io import wavfile
import scipy.fftpack as fft 
import matplotlib.pyplot as plt
import os 
import sys
import subprocess
import matplotlib.animation as animation
import numpy as np
import math
import multiprocessing



sample_rate, x = wavfile.read(sys.argv[1])

nb_bits = 16

max_bit_val = float( 2 ** (nb_bits - 1))

if sys.argv[2] == "single":
	samples = x / (max_bit_val + 1.0)
elif sys.argv[2] == "dual":
	samples = x.T[0] / (max_bit_val + 1.0)
else:
	print("SCREEE", sys.argv[2])

#print(samples, samples[0])
#plt.plot(samples)

#samples is a list of frequencies, sampled at sample_rate/second
#we want each fft to capture a certain # of seconds of sample. 
#so we want each FRAME_RATE # of frames to capture sample_rate # of frequencies
#so each frame of the animation contains sample_rate/frame_rate # of frequencies
#and the total # of frames is frame_rate * song length in seconds
# song length in seconds = # of frequency measurements/sample_rate

song_length = int(len(samples) / sample_rate)
frames = []
frame_rate = 30
frame_len = int(sample_rate / frame_rate) #int(len(samples)/(sample_rate * frame_rate))

for i in range(frame_rate * song_length):
 	frames.append(samples[i*frame_len:(i+1)*frame_len])

print("frequency samples per frame=",frame_len)
dropped = (len(samples)-(frame_len * frame_rate * song_length))/frame_len
print(frame_len * frame_rate * song_length,len(samples), f"dropping the last {dropped} frames")


if sys.argv[3] == "full":
	RUNTIME = math.floor(song_length)
else:
	RUNTIME = int(sys.argv[3])

MAX_DB = 150
MIN_DB_CUTOFF = 0.25
BOOST = 20
BUMP = 1

DUAL_BUMP = 5

FREQ_RANGE = 60 #50 #75

def fft_worker(i):
	if(i%500 == 0):
		print("Frame #",i,"/",frame_rate*RUNTIME)

	val = fft.fft(frames[i])
	half_len = int(len(val)/2)
	res = abs(val)[:FREQ_RANGE] #take the first FREQ_RANGE values because that's what we care about
	res = np.append(res,[res[0]]) #complete the loop

	res = [MAX_DB if x>MAX_DB else x for x in res] #filter down to maximum value

	relative_max = max(res)
	res = [BUMP if x<relative_max*MIN_DB_CUTOFF else x for x in res] #filter out small values, but make it a small bump so the graph doesn't look as bad

	res = [x + BOOST for x in res] #boosto

	q.put([i,res])

	return

#Set up our datatypes for multiprocessing
q = multiprocessing.Queue()

fft_dict = [0]*frame_rate*RUNTIME #gotta love dynamic typing... this is defintely not illegal. I could initialize this array with empty frames, but what's the point when python literally does not care
WORKERS = 8

#send workers in for each i in batches of 8
for i in range(int(frame_rate*RUNTIME/WORKERS)):

	threads = []
	for x in range(WORKERS):
		t = multiprocessing.Process(target=fft_worker,args=[WORKERS*i+x])
		t.start()
		threads.append(t)
		
	for thread in threads:
		thread.join()
		thread.close()

	while(not q.empty()):
		i, processed_frame = q.get()
		fft_dict[i] = processed_frame  #what do you mean python is a hacky language??

print("Finished fft ing ")


graph_x = [2*np.pi/FREQ_RANGE*i for i in range(FREQ_RANGE + 1)] #create x range

def update(i):
	processed_frame = fft_dict[i]

	ax.clear()
	ax.set_ylim(0, MAX_DB + BOOST + DUAL_BUMP)
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.grid(False)
	ax.axis('off')

	ax.plot(graph_x, processed_frame, 'skyblue') #my usual colour scheme <3
	ax.plot(graph_x, [x+DUAL_BUMP for x in processed_frame], 'pink')



fig,ax = plt.subplots(subplot_kw=dict(polar=True))
print("Generating animation")
anim = animation.FuncAnimation(fig, update, interval=1/frame_rate, frames=frame_rate*RUNTIME, repeat=False) #, init_func=init, blit=True)

if sys.argv[4]=="show":
	plt.show()
elif sys.argv[4] == "save":
	anim.save(sys.argv[1][:-4] + "_spec.mp4", fps=frame_rate)

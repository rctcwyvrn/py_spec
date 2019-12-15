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
#so we want each 120 frames to capture sample_rate # of frequencies
#so each frame contains sample_rate/frame_rate # of frequencies
#and the total # of frames is frame_rate * song length in seconds
# song length in seconds = # o frequency measurements/sample_rate

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
MIN_DB = 10
BOOST = 10

#plt.plot(frames[0])
#plt.show()

#assert(frame_len * frame_rate * song_length == len(samples))

# samples/frame * frames/second * seconds/song


#frame length of sample_rate
# for i in range(int(len(samples)/sample_rate)):
# 	frames.append(samples[i*sample_rate:(i+1)*sample_rate])

#print(len(frames), frames[0])

#audio_p = subprocess.Popen(["./start_vlc.sh",sys.argv[1]])
#audio_p = subprocess.Popen(["vlc",sys.argv[1],"&"])

#print(len(frames)/(frame_rate))

# total = 0
# for frame in frames[:frame_rate*RUNTIME]:
# 	total+=len(frame)
# 	val = fft(frame)
# 	half_len = int(len(val)/2)

# 	plt.plot(abs(val[:(half_len-1)]),'r')
# 	plt.ylim(top = 50, bottom=0)

# 	#plt.plot(frame)
# 	#plt.ylim(top = 1, bottom=-1)

# 	plt.pause(1/frame_rate)
# 	plt.clf()

def avg(xs):
	return sum(xs)/bar_width

bar_width = 1
def bar(ar):
	splices = []
	for i in range(0,len(ar),bar_width):
		splices.append(ar[i:i+bar_width])

	#print("splices",splices)
	return np.array([avg(x) for x in splices])
	#return np.array(list(set([math.floor(x/bar_width)*bar_width for x in ar])))


def fft_worker(i):
	if(i%50 == 0):
		print("Frame #",i,"/",frame_rate*RUNTIME)

	val = fft.fft(frames[i])
	# #print(frames[i],val)
	half_len = int(len(val)/2)
	res = abs(val)[:75] + BOOST #take the first 75 values because that's what we care about. also scale it up so it looks nicer
	res = np.append(res,[res[0]]) #complete the loop
	res = [MAX_DB if x>MAX_DB else x for x in res] #filter down to maximum value
	res = [BOOST if x<=BOOST+MIN_DB else x for x in res] #filter down to maximum value



	#res = abs(val[:(half_len-1)])
	#print(len(res))
	#print(res)

	#points = np.array([x,res]).T.reshape(-1,1,2)
	#segments = np.concatenate([points[:-1], points[1:]], axis=1)
	#lc = LineCollection(segments, cmap=cmap, norm=norm)
	#lc.set_array(x)
	#lc.set_linewidth(3)
	#q.put([i,lc])

	#print("done fft, putting into queue")
	q.put([i,res])

	#q.put([i,abs(val[:(half_len-1)])])
	#print("returning",i)

	return

#make queue
q = multiprocessing.Queue()

fft_dict = [0]*frame_rate*RUNTIME
WORKERS = 8

#max_db = 0
#send workers in for each i in batches of 8
for i in range(int(frame_rate*RUNTIME/WORKERS)):

	threads = []
	#print("upping i to i=",i)
	for x in range(WORKERS):
		#print("making worker #",x+1)
		t = multiprocessing.Process(target=fft_worker,args=[WORKERS*i+x])
		t.start()
		threads.append(t)
		
	for thread in threads:
		thread.join()
		#print("got one back")
		thread.close()
	#print("everyones back")

	while(not q.empty()):
		i,val = q.get()

		#if max(val) > max_db:
		#	max_db = max(val)

		fft_dict[i] = val

print("Finished fft ing ")
#print("max db found was ",max_db)


graph_x = [2*np.pi/75*i for i in range(76)] #create x range

#frame in this case is the audio frame
def update(i):
	val = fft_dict[i]
	#x = [bar_width*i for i in range(len(val))]
	#x = [2*np.pi/len(val)*i for i in range(len(val))] #create x range

	#print(x)
	ax.clear()
	#ax.set_ylim(0,max_db)
	ax.set_ylim(0, MAX_DB)
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.grid(False)
	ax.axis('off')
	#ax.set_ylabel("loudness? idk lol")
	#ax.set_xlabel("hz")
	#colors = plt.cm.viridis(val/150)

	#ax.bar(x=x,height=val, color=colors, bottom =0.0, alpha=0.5)

	#lc = fft_dict[i]
	#ax.add_collection(lc)

	# ax.plot(graph_x[:10],val[:10], 'r')
	# ax.plot(graph_x[10:20],val[10:20], 'g')
	# ax.plot(graph_x[20:30],val[20:30], 'c')
	# ax.plot(graph_x[30:40],val[30:40], 'm')
	# ax.plot(graph_x[40:50],val[40:50], 'y')
	# ax.plot(graph_x[50:60],val[50:60], 'b')
	# ax.plot(graph_x[60:75],val[60:75], 'k')

	ax.plot(graph_x,val, 'c')

	#val_upper


fig,ax = plt.subplots(subplot_kw=dict(polar=True))
print("Generating animation")
anim = animation.FuncAnimation(fig, update, interval=1/frame_rate, frames=frame_rate*RUNTIME, repeat=False) #, init_func=init, blit=True)

if sys.argv[4]=="show":
	plt.show()
elif sys.argv[4] == "save":
	anim.save(sys.argv[1][:-4] + "_spec.mp4", fps=frame_rate)

#plt.show()
#audio_p.kill()
#plt.show()
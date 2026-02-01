import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile 
from scipy.signal.windows import hann

fs, data = wavfile.read('/home/lily/Documents/test.wav') # load the data
first_channel = data.T[0] # this is a two channel soundtrack, I get the first track
normalized = first_channel / 2**16. # this is 16-bit track, b is now normalized on [-1,1)
frame_len = 4000
window = hann(frame_len)
fft_data = abs(fft(window * normalized[:frame_len])) # calculate fourier transform (complex numbers list)
fft_truncated = fft_data[:100]
fft_normalized = fft_truncated / max(fft_truncated)

plt.plot(fft_normalized)
plt.show()
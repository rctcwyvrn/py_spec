https://youtu.be/i87schwHTNw

You need a `.wav` audio file

Run py_spec with `python py_spec file.wav <dual|single> <runtime> <show|save>`, which will output `file_spec.mp4`.

Run `file` to see if the `.wav` is mono (single channel) or stereo (dual channel)

`create.sh` runs py_spec and runs ffmpeg to combine the audio and the video.

It's a mess, take a look if you want. Some constants you can change are:
- The framerate (which messes up other things for some reason, so watch out for that I guess)
- MAX_DB. Turning this up will make the quieter look smaller by allowing the louder sounds to actually show their loudness.
- BOOST. Turning this up will make the circle's radius larger
- The colour at line 209 if you really want
- WORKERS. The number of multithreaded workers to do the FFT. It doesn't really matter since a majority of the time is spent waiting for matplotlib to save the animation anyway

Requirements:
- scipy
- matplotlib
- numpy

Somewhere in the mess of commented out blocks of code is the settings to turn py_spec into a bar graph style visualization
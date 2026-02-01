echo "Usage: ./create.sh basename [dual|single] time output_filename"
python3 py_spec.py $1.wav $2 $3 save
ffmpeg -i $1_spec.mp4 -i $1.wav -c:v copy -c:a aac -strict experimental $4

uv run manim --fps 30 -qh main.py CreateVisual
# yes | ffmpeg -i ./media/videos/main/1080p30/CreateVisual.mp4 -i /home/lily/Documents/test.wav -c:v copy -c:a aac -strict experimental out.mp4
yes | ffmpeg -i ./media/videos/main/1080p30/CreateVisual.mp4 -i /home/lily/Documents/draft-2-shorter.wav -c:v copy -c:a aac -strict experimental out.mp4
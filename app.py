import os
import subprocess
from flask import Flask, render_template, request, send_file
from gtts import gTTS

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'video' not in request.files:
        return "No video uploaded", 400
    
    video = request.files['video']
    video.save("input.mp4")

    # Form settings
    flip = request.form.get('flip')
    speed = request.form.get('speed')
    pitch = request.form.get('pitch')
    red_box = request.form.get('red_box')
    dubbing_text = request.form.get('dubbing_text')

    # Video Filters
    v_filters = []
    if flip: v_filters.append("hflip")
    if speed: v_filters.append("setpts=0.95*PTS")
    if red_box: v_filters.append("drawbox=y=ih-100:color=red@0.5:width=iw:height=100:t=fill")
    
    vf_str = ",".join(v_filters) if v_filters else "null"

    # Audio Handling (AI Dubbing)
    audio_input = ""
    if dubbing_text:
        tts = gTTS(text=dubbing_text, lang='my')
        tts.save("voice.mp3")
        audio_input = "-i voice.mp3 -map 0:v:0 -map 1:a:0 -shortest"
    else:
        audio_input = "-map 0:a?"

    # Execute FFmpeg
    cmd = f'ffmpeg -i input.mp4 {audio_input} -vf "{vf_str}" -y output.mp4'
    subprocess.run(cmd, shell=True)

    return send_file("output.mp4", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

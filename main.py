import os
from flask import Flask, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_audio_as_mp3(url):
    tmpl = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': tmpl,
        'noplaylist': True,
        'postprocessors': [{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = os.path.splitext(ydl.prepare_filename(info))[0]
        return base + ".mp3"

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        url = request.form['youtube_url']
        try:
            mp3 = download_audio_as_mp3(url)
            @after_this_request
            def cleanup(response):
                os.remove(mp3)
                return response
            return send_file(mp3, as_attachment=True)
        except Exception as e:
            return f"<p>Error: {e}</p>", 400
    return '''
        <form method="POST">
            YouTube URL: <input name="youtube_url" size="50">
            <button type="submit">Download MP3</button>
        </form>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, render_template, request, redirect, url_for
from google.cloud import storage, speech_v1p1beta1 as speech
from mutagen.mp3 import MP3

BUCKET_NAME = "notesai"
BLOB_NAME = "audio"

app = Flask(__name__)
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(BLOB_NAME)

speech_client = speech.SpeechClient()
speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code="en-US",
    )
speech_audio = speech.RecognitionAudio(uri=f"gs://{BUCKET_NAME}/{BLOB_NAME}")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/generate", methods=["POST"])
def generate():
    # TODO: check for file length
    if "audio" not in request.files:
        return redirect(url_for("home"), code=400)
    file = request.files["audio"]
    if not file.filename.endswith(".mp3"):
        return redirect(url_for("home"), code=400)
    upload_audio(file)
    text = transcribe_audio()
    # call api summarize. returns bullet
    return redirect(url_for("home"), code=200)

def upload_audio(file):
    blob.upload_from_file(file)
    speech_config.sample_rate_hertz = MP3(file).info.sample_rate

def transcribe_audio():
    # TODO: determine appropriate timeout
    response = speech_client.long_running_recognize(config=speech_config, audio=speech_audio).result(timeout=20)
    transcript = ""
    for result in response.results:
        transcript += f"\n{result.alternatives[0].transcript}"
    # TODO: check for transcript length
    return transcript

if __name__ == "__main__":
    app.run(debug=True)
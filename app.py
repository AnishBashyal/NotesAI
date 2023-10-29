from flask import Flask, render_template, request, redirect, url_for, jsonify
from google.cloud import storage, speech_v1p1beta1 as speech
from mutagen.mp3 import MP3
from pymediainfo import MediaInfo
from moviepy import editor
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()
BUCKET_NAME = "notesai"
BLOB_NAME = "audio"
TEMP_FILE_NAME = "blob"

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


@app.route("/summary", methods=["POST"])
def generate():
    if request.method == "POST":
        # TODO: check for file length
        if "audio" not in request.files:
            return redirect(url_for("home"), code=400)
        file = request.files["audio"]
        upload_audio(file)
        text = transcribe_audio()
        summary = make_summary(text)
        return render_template("summary.html", summary=summary)


def upload_audio(file):
    file.save(TEMP_FILE_NAME)
    info = MediaInfo.parse(TEMP_FILE_NAME)
    isVideo = False
    for track in info.tracks:
        if track.track_type == "Video":
            isVideo = True
            break
    if isVideo:
        video = editor.VideoFileClip(TEMP_FILE_NAME)
        audio = video.audio
    else:
        audio = editor.AudioFileClip(TEMP_FILE_NAME)
    mp3_name = f"{TEMP_FILE_NAME}.mp3"
    audio.write_audiofile(mp3_name)
    speech_config.sample_rate_hertz = MP3(mp3_name).info.sample_rate
    blob.upload_from_filename(mp3_name)


def transcribe_audio():
    # TODO: determine appropriate timeout
    response = speech_client.long_running_recognize(
        config=speech_config, audio=speech_audio
    ).result(timeout=90)
    transcript = ""
    for result in response.results:
        transcript += f"\n{result.alternatives[0].transcript}"
    # TODO: check for transcript length
    print(transcript)
    return transcript


def make_summary(transcript):
    llm = OpenAI(temperature=0)

    prompt_template = PromptTemplate(
        input_variables=["lecture"],
        template="Make informative, concise, short and accurate notes of the following lecture. The lecture : {lecture}",
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(transcript)
    return response


if __name__ == "__main__":
    app.run(debug=True)

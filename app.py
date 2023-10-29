from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from google.cloud import storage, speech_v1p1beta1 as speech
from mutagen.mp3 import MP3
from pymediainfo import MediaInfo
from moviepy import editor
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from routes import main
from os import environ as env
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
import requests

# import html, re

load_dotenv()
BUCKET_NAME = "notesai"
BLOB_NAME = "audio"
TEMP_FILE_NAME = "blob"

app = Flask(__name__)
app.register_blueprint(main)

app.secret_key = env.get("APP_SECRET_KEY")

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(BLOB_NAME)

speech_client = speech.SpeechClient()
speech_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.MP3,
    language_code="en-US",
)
speech_audio = speech.RecognitionAudio(uri=f"gs://{BUCKET_NAME}/{BLOB_NAME}")

llm = ChatOpenAI(temperature=0)

prompt_template = PromptTemplate(
    input_variables=["lecture"],
    template="Please make informative and concise notes of the following lecture. The lecture: {lecture}.",
)

chain = LLMChain(llm=llm, prompt=prompt_template)


# def remove_special_chars(strings):
#     cleaned_strings = []
#     for text in strings:
#         cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
#         cleaned_strings.append(cleaned_text)
#     return cleaned_strings

# app.jinja_env.filters['remove_special_chars'] = remove_special_chars

# @app.route('/test')
# def test():
#     strings_array = [
#         "String 1, with special characters! @#",
#         "Another string with *&^%$ special characters",
#         "String without special characters"
#     ]
#     return render_template('test.html', strings_array=strings_array)


@app.route("/")
def home():
    return render_template("home.html", title="NotesAI", session=session.get("user"))


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
        # print("SUMMARY", summary)
        summary = summary.split("- ")[1:]
        return render_template(
            "summary.html",
            summary=summary,
            title="Summary",
            session=session.get("user"),
        )


@app.route("/notes", methods=["GET"])
def get_notes():
    if not session:
        return redirect(url_for("home"))
    user_id = session.get("user")["userinfo"]["sub"]
    base_url = "http://localhost:3000/"
    api_url = url_for("main.user_notes", user_id=user_id)
    response = requests.get(base_url + api_url)

    api_data = response.json() if response else None
    # print(api_data)
    return render_template(
        "lectures.html", title="Notes", session=session.get("user"), notes=api_data
    )


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
    ).result(timeout=600)
    transcript = ""
    for result in response.results:
        transcript += f"\n{result.alternatives[0].transcript}"
    # TODO: check for transcript length
    print(transcript)
    return transcript


def make_summary(transcript):
    response = chain.run(transcript)
    print(response)
    return response


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))

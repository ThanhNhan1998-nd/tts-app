from flask import Flask, render_template, request, send_file
import edge_tts
import asyncio
import os

app = Flask(__name__)

async def generate_tts(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        voice = request.form["voice"]

        asyncio.run(generate_tts(text, voice))
        return send_file("output.mp3", mimetype="audio/mpeg")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
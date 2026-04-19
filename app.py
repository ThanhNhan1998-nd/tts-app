from flask import Flask, render_template, request, send_file, jsonify
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)

OUTPUT_DIR = "audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def generate_tts(text, voice, rate, filename):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tts", methods=["POST"])
def tts():
    text = request.form["text"]
    voice = request.form["voice"]
    rate = request.form["rate"]

    filename = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp3")

    asyncio.run(generate_tts(text, voice, rate, filename))

    return jsonify({
    "audio": filename.replace("\\", "/")
})
    })

@app.route("/audio/<path:filename>")
def serve_audio(filename):
    return send_file(filename, mimetype="audio/mpeg")

@app.route("/download/<path:filename>")
def download(filename):
    return send_file(
        filename,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="tts.mp3"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
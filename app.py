from flask import Flask, render_template, request, send_file, jsonify
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)

# ✔ Render nên dùng /tmp để tránh mất file
OUTPUT_DIR = "/tmp/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def generate_tts(text, voice, rate, filename):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text", "")
    voice = request.form.get("voice", "vi-VN-HoaiMyNeural")
    rate = request.form.get("rate", "+0%")

    # tạo file unique
    filename = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp3")

    # tạo audio
    asyncio.run(generate_tts(text, voice, rate, filename))

    # trả về link đúng route
    return jsonify({
        "audio": "/audio/" + os.path.basename(filename)
    })


@app.route("/audio/<path:filename>")
def serve_audio(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    return send_file(file_path, mimetype="audio/mpeg")


@app.route("/download/<path:filename>")
def download(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    return send_file(
        file_path,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="tts.mp3"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
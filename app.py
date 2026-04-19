from flask import Flask, render_template, request, send_file, jsonify, session
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)
app.secret_key = "tts-ultimate-key"

OUTPUT_DIR = "/tmp/tts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# PRESET VOICES
# =========================
VOICES = {
    "female_north": "vi-VN-HoaiMyNeural",
    "male_north": "vi-VN-NamMinhNeural"
}


# =========================
# TTS ENGINE
# =========================
async def tts_engine(text, voice, rate, path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{rate}%"
    )
    await communicate.save(path)


# =========================
# HOME
# =========================
@app.route("/")
def home():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")


# =========================
# TTS API
# =========================
@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = request.form.get("text", "").strip()
        voice_key = request.form.get("voice", "female_north")
        rate = request.form.get("rate", "0")

        if not text:
            return jsonify({"error": "Text is empty"}), 400

        voice = VOICES.get(voice_key, VOICES["female_north"])

        file_id = str(uuid.uuid4())
        filename = f"{file_id}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        asyncio.run(tts_engine(text, voice, rate, filepath))

        audio_url = f"/audio/{filename}"

        # save history (session)
        history = session.get("history", [])
        history.insert(0, {"text": text[:50], "file": filename})
        session["history"] = history[:10]

        return jsonify({
            "audio": audio_url,
            "file": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# AUDIO SERVE
# =========================
@app.route("/audio/<filename>")
def audio(filename):
    return send_file(
        os.path.join(OUTPUT_DIR, filename),
        mimetype="audio/mpeg"
    )


# =========================
# DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_file(
        os.path.join(OUTPUT_DIR, filename),
        as_attachment=True,
        download_name="tts-ultimate.mp3"
    )


# =========================
# HISTORY API
# =========================
@app.route("/history")
def history():
    return jsonify(session.get("history", []))


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
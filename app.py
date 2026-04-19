from flask import Flask, render_template, request, send_file
import edge_tts
import asyncio

app = Flask(__name__)

VOICE = "vi-VN-HoaiMyNeural"

async def generate_tts(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("output.mp3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        asyncio.run(generate_tts(text))
        return send_file("output.mp3", as_attachment=False)
    return render_template("index.html")

if __name__ == "__main__":
    import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
from flask import Flask, request, send_file, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def home():
    return {"status": "API running!"}

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    video_url = data.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Unique filename prefix
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    try:
        # Run yt-dlp as a subprocess to download best mp4 video
        command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_template,
            video_url,
        ]
        subprocess.run(command, check=True)

        # Find the downloaded file
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(file_id)]
        if not files:
            return jsonify({"error": "Download failed"}), 500

        filepath = os.path.join(DOWNLOAD_DIR, files[0])
        return send_file(filepath, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Download error: {e}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

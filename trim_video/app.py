from flask import Flask, request, jsonify
import json
import subprocess
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

app = Flask(__name__)

s3_client = boto3.client(
    "s3",
    region_name="eu-north-1",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)

S3_BUCKET = "trim-videos"
PRESIGNED_URL_EXPIRATION = int(os.environ.get("PRESIGNED_URL_EXPIRATION", 3600))
YTDLP_BINARY = os.path.join(os.getcwd(), "yt-dlp.exe")


def download_youtube_video(youtube_url, output_path):
    cmd = [
        YTDLP_BINARY,
        "-f",
        "best[ext=mp4]/best",
        "--no-playlist",
        "-o",
        output_path,
        youtube_url,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@app.route("/", methods=["GET"])
def gethello():
    return jsonify(
        {
            "message": "Hello world!",
        }
    )


@app.route("/trim", methods=["POST"])
def trim_video():
    try:
        body = request.get_json(force=True)

        video_url = body.get("video_url")
        start_ms = body.get("start")
        end_ms = body.get("end")
        is_youtube_url = body.get("is_youtube_url") == "true"

        if not all([video_url, start_ms is not None, end_ms is not None]):
            return jsonify({"error": "Missing parameters"}), 400

        start_sec = start_ms / 1000
        end_sec = end_ms / 1000
        duration = end_sec - start_sec

        if duration <= 0:
            return jsonify({"error": "Invalid duration"}), 400

        uid = str(uuid.uuid4())
        input_file = video_url
        downloaded_file = None

        if is_youtube_url:
            downloaded_file = f"/tmp/input_{uid}.mp4"
            download_youtube_video(video_url, downloaded_file)
            input_file = downloaded_file

        output_file = f"/tmp/output_{uid}.mp4"
        s3_key = f"trimmed-videos/{uid}.mp4"

        subprocess.run(
            [
                "ffmpeg",
                "-ss",
                str(start_sec),
                "-i",
                input_file,
                "-t",
                str(duration),
                "-c",
                "copy",
                "-y",
                output_file,
            ],
            check=True,
        )

        s3_client.upload_file(
            output_file, S3_BUCKET, s3_key, ExtraArgs={"ContentType": "video/mp4"}
        )

        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRATION,
        )

        return jsonify({"message": "success", "url": presigned_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
